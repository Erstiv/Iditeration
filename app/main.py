"""Idideration — AI Marketing Strategy Platform"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import init_db, SessionLocal
from app.models import User, BibleEntry, BibleScope, AgentNote, ResearchBrief  # noqa: F401 — ensures table is registered
from app.routes.projects import router as projects_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("idideration")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    _ensure_default_user()
    _seed_marketing_bible()
    logger.info("Idideration ready.")
    yield


app = FastAPI(title="Idideration", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.include_router(projects_router)


def _ensure_default_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "elliot@idideration.com").first()
        if not user:
            user = User(email="elliot@idideration.com", name="Elliot", is_admin=True)
            db.add(user)
            db.commit()
            logger.info("Created default user.")
    finally:
        db.close()


def _seed_marketing_bible():
    """Load marketing bible seed data if the global bible is empty."""
    db = SessionLocal()
    try:
        count = db.query(BibleEntry).filter(BibleEntry.scope == BibleScope.GLOBAL).count()
        if count > 0:
            logger.info(f"Marketing Bible already has {count} entries, skipping seed.")
            return

        import json
        seed_path = Path(__file__).parent.parent / "marketing_bible_seed" / "seed_data.json"
        if not seed_path.exists():
            logger.warning("No seed_data.json found, skipping bible seed.")
            return

        with open(seed_path) as f:
            seed_data = json.load(f)

        for entry in seed_data:
            from app.models import BibleCategory
            try:
                cat = BibleCategory(entry["category"])
            except ValueError:
                logger.warning(f"Unknown category: {entry['category']}, skipping.")
                continue

            be = BibleEntry(
                scope=BibleScope.GLOBAL,
                project_id=None,
                category=cat,
                title=entry["title"],
                content=entry["content"],
                entry_data=entry.get("entry_data"),
                source="seed",
            )
            db.add(be)

        db.commit()
        logger.info(f"Seeded Marketing Bible with {len(seed_data)} entries.")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    from app.config import APP_HOST, APP_PORT
    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)
