"""
Marketing Bible Tool — programmatic read/write interface for the knowledge base.
Used by all agents to read global marketing frameworks and read/write project-specific data.
Mirrors Cassian's StoryBibleTool pattern.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import BibleEntry, BibleScope, BibleCategory


class MarketingBibleTool:
    """Interface for agents to interact with the Marketing Bible (global) and Product Bible (per-project)."""

    def __init__(self, db: Session, project_id: Optional[int] = None):
        self.db = db
        self.project_id = project_id

    # ─── Read Operations ────────────────────────────────────

    def get_global_entries(self, category: Optional[BibleCategory] = None) -> list[BibleEntry]:
        q = self.db.query(BibleEntry).filter(
            BibleEntry.scope == BibleScope.GLOBAL,
            BibleEntry.is_active == True,
        )
        if category:
            q = q.filter(BibleEntry.category == category)
        return q.order_by(BibleEntry.sort_order, BibleEntry.title).all()

    def get_project_entries(self, category: Optional[BibleCategory] = None) -> list[BibleEntry]:
        if not self.project_id:
            return []
        q = self.db.query(BibleEntry).filter(
            BibleEntry.scope == BibleScope.PROJECT,
            BibleEntry.project_id == self.project_id,
            BibleEntry.is_active == True,
        )
        if category:
            q = q.filter(BibleEntry.category == category)
        return q.order_by(BibleEntry.sort_order, BibleEntry.title).all()

    def get_all_project_entries(self) -> list[BibleEntry]:
        return self.get_project_entries()

    def search(self, keyword: str, scope: Optional[BibleScope] = None) -> list[BibleEntry]:
        q = self.db.query(BibleEntry).filter(
            BibleEntry.is_active == True,
            (BibleEntry.title.ilike(f"%{keyword}%") | BibleEntry.content.ilike(f"%{keyword}%")),
        )
        if scope:
            q = q.filter(BibleEntry.scope == scope)
        if scope == BibleScope.PROJECT and self.project_id:
            q = q.filter(BibleEntry.project_id == self.project_id)
        return q.all()

    # ─── Write Operations (Product Bible only) ──────────────

    def add_entry(
        self,
        category: BibleCategory,
        title: str,
        content: str,
        source: str = "manual",
        entry_data: Optional[dict] = None,
    ) -> BibleEntry:
        entry = BibleEntry(
            scope=BibleScope.PROJECT,
            project_id=self.project_id,
            category=category,
            title=title,
            content=content,
            source=source,
            entry_data=entry_data,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def add_entries_bulk(self, entries: list[dict], source: str = "manual") -> list[BibleEntry]:
        created = []
        for e in entries:
            cat = e.get("category")
            if isinstance(cat, str):
                cat = BibleCategory(cat)
            entry = BibleEntry(
                scope=BibleScope.PROJECT,
                project_id=self.project_id,
                category=cat,
                title=e["title"],
                content=e["content"],
                source=source,
                entry_data=e.get("entry_data"),
            )
            self.db.add(entry)
            created.append(entry)
        self.db.commit()
        for entry in created:
            self.db.refresh(entry)
        return created

    def update_entry(self, entry_id: int, **kwargs) -> Optional[BibleEntry]:
        entry = self.db.query(BibleEntry).filter(BibleEntry.id == entry_id).first()
        if not entry:
            return None
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete_entry(self, entry_id: int) -> bool:
        entry = self.db.query(BibleEntry).filter(BibleEntry.id == entry_id).first()
        if not entry:
            return False
        entry.is_active = False
        self.db.commit()
        return True

    # ─── Prompt Formatting ──────────────────────────────────

    def to_prompt_text(self, scope: BibleScope, categories: Optional[list[BibleCategory]] = None) -> str:
        """Format bible entries as text for LLM prompts."""
        if scope == BibleScope.GLOBAL:
            entries = self.get_global_entries()
        else:
            entries = self.get_project_entries()

        if categories:
            entries = [e for e in entries if e.category in categories]

        if not entries:
            return f"=== {'MARKETING' if scope == BibleScope.GLOBAL else 'PRODUCT'} BIBLE ===\n(No entries yet)\n"

        # Sort directives first, then alphabetically by category
        def _sort_key(e):
            if e.category.value == "directives":
                return ("0_directives", e.sort_order)
            return (e.category.value, e.sort_order)

        lines = [f"=== {'MARKETING' if scope == BibleScope.GLOBAL else 'PRODUCT'} BIBLE ==="]
        current_cat = None
        for entry in sorted(entries, key=_sort_key):
            if entry.category != current_cat:
                current_cat = entry.category
                if current_cat.value == "directives":
                    lines.append("\n!!! MANDATORY DIRECTIVES (ALL AGENTS MUST FOLLOW) !!!")
                    lines.append("The following are hard constraints. Do NOT contradict, ignore,")
                    lines.append("or work around these rules in any output.\n")
                else:
                    lines.append(f"\n--- {current_cat.value.replace('_', ' ').title()} ---")

            if current_cat.value == "directives":
                lines.append(f"  ⛔ [{entry.title}]")
            else:
                lines.append(f"  [{entry.title}]")
            # Truncate long content for prompt context
            content = entry.content
            if len(content) > 500:
                content = content[:497] + "..."
            lines.append(f"  {content}")
            lines.append("")

        lines.append(f"=== {len(entries)} entry(ies) total ===")
        return "\n".join(lines)

    def to_full_prompt_text(self, scope: BibleScope) -> str:
        """Full untruncated bible text for deep-read agents."""
        if scope == BibleScope.GLOBAL:
            entries = self.get_global_entries()
        else:
            entries = self.get_project_entries()

        lines = [f"=== {'MARKETING' if scope == BibleScope.GLOBAL else 'PRODUCT'} BIBLE (FULL) ==="]
        current_cat = None
        for entry in sorted(entries, key=lambda e: (e.category.value, e.sort_order)):
            if entry.category != current_cat:
                current_cat = entry.category
                lines.append(f"\n--- {current_cat.value.replace('_', ' ').title()} ---")
            lines.append(f"\n  ## {entry.title}")
            lines.append(f"  {entry.content}")
            lines.append("")

        lines.append(f"=== {len(entries)} entry(ies) total ===")
        return "\n".join(lines)
