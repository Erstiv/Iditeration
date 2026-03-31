import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class ProjectType(enum.Enum):
    TV_SERIES = "tv_series"
    FILM = "film"
    CPG = "cpg"
    APP = "app"
    BRAND = "brand"
    IDEA = "idea"
    OTHER = "other"


class RunStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentName(enum.Enum):
    RESEARCH_AGENT = "research_agent"
    INTAKE_ANALYST = "intake_analyst"
    BEHAVIORAL_SCIENTIST = "behavioral_scientist"
    PSYCHOMETRICS_EXPERT = "psychometrics_expert"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    SOCIAL_STRATEGIST = "social_strategist"
    CHIEF_STRATEGIST = "chief_strategist"
    CREATIVE_DIRECTOR = "creative_director"
    STAKEHOLDER_AGENT = "stakeholder_agent"


class BibleScope(enum.Enum):
    GLOBAL = "global"       # Marketing Bible — shared across all projects
    PROJECT = "project"     # Product Bible — per-project knowledge


class BibleCategory(enum.Enum):
    # Marketing Bible categories (global)
    PSYCHOMETRICS = "psychometrics"
    NEUROSCIENCE = "neuroscience"
    BEHAVIORAL_ECONOMICS = "behavioral_economics"
    SOCIAL_MEDIA = "social_media"
    GAME_THEORY = "game_theory"
    DEMOGRAPHICS = "demographics"
    CONTENT_STRATEGY = "content_strategy"
    PRICING = "pricing"
    BRAND_BUILDING = "brand_building"
    FRAMEWORKS = "frameworks"
    # Product Bible categories (per-project)
    DIRECTIVES = "directives"  # System-level constraints — agents MUST follow these
    PRODUCT_OVERVIEW = "product_overview"
    STAKEHOLDER_INPUT = "stakeholder_input"
    RESEARCH_FINDINGS = "research_findings"
    AUDIENCE_SEGMENTS = "audience_segments"
    COMPETITIVE_DATA = "competitive_data"
    SOCIAL_DATA = "social_data"
    STRATEGY = "strategy"
    CREATIVE = "creative"
    NARRALYTICA_DATA = "narralytica_data"


# ─── Core Models ────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    description = Column(Text)
    # For media products — link to Narralytica
    narralytica_show_id = Column(Integer, nullable=True)
    # Raw product data (pasted text, links, notes)
    raw_data = Column(Text)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="projects")
    bible_entries = relationship("BibleEntry", back_populates="project", foreign_keys="BibleEntry.project_id")
    crew_runs = relationship("CrewRun", back_populates="project")
    stakeholder_questions = relationship("StakeholderQuestion", back_populates="project")
    output_documents = relationship("OutputDocument", back_populates="project")


# ─── Knowledge Base ─────────────────────────────────────────

class BibleEntry(Base):
    __tablename__ = "bible_entries"

    id = Column(Integer, primary_key=True)
    scope = Column(SQLEnum(BibleScope), nullable=False)
    # NULL for global entries, set for project-specific entries
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    category = Column(SQLEnum(BibleCategory), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    # Structured data (JSON) for machine-readable content
    entry_data = Column(JSON, nullable=True)
    # Who/what created this entry
    source = Column(String(100), default="manual")  # manual, agent:{name}, seed
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="bible_entries", foreign_keys=[project_id])


# ─── Crew Runs ──────────────────────────────────────────────

class CrewRun(Base):
    __tablename__ = "crew_runs"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(SQLEnum(RunStatus), default=RunStatus.PENDING)
    # Which agents to run (JSON list of agent names)
    agents_to_run = Column(JSON, nullable=False)
    # Config snapshot at run time
    run_config = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="crew_runs")
    agent_runs = relationship("AgentRun", back_populates="crew_run", order_by="AgentRun.sequence_order")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True)
    crew_run_id = Column(Integer, ForeignKey("crew_runs.id"), nullable=False)
    agent_name = Column(SQLEnum(AgentName), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    status = Column(SQLEnum(RunStatus), default=RunStatus.PENDING)
    # Model used (flash vs pro)
    model_used = Column(String(100))
    # The full prompt sent to the model
    input_prompt = Column(Text, nullable=True)
    # Structured JSON output from the agent
    output_json = Column(JSON, nullable=True)
    # Raw text output (if any)
    output_raw = Column(Text, nullable=True)
    # Token usage tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    # Cost tracking (estimated)
    cost_usd = Column(Float, default=0.0)
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    # One-time guidance for a rerun (not persisted to Bible)
    rerun_guidance = Column(Text, nullable=True)

    crew_run = relationship("CrewRun", back_populates="agent_runs")
    notes = relationship("AgentNote", back_populates="agent_run", order_by="AgentNote.created_at")


# ─── Agent Notes (Ask / Refocus Q&A) ──────────────────────

class AgentNote(Base):
    __tablename__ = "agent_notes"

    id             = Column(Integer, primary_key=True)
    crew_run_id    = Column(Integer, ForeignKey("crew_runs.id"), nullable=False)
    agent_run_id   = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    project_id     = Column(Integer, ForeignKey("projects.id"), nullable=False)
    question       = Column(Text, nullable=False)
    answer         = Column(Text, nullable=False)
    model_used     = Column(String(100))
    input_tokens   = Column(Integer, default=0)
    output_tokens  = Column(Integer, default=0)
    cost_usd       = Column(Float, default=0.0)
    bible_entry_id = Column(Integer, ForeignKey("bible_entries.id"), nullable=True)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    agent_run = relationship("AgentRun", back_populates="notes")


# ─── Stakeholder Management ────────────────────────────────

class StakeholderQuestion(Base):
    __tablename__ = "stakeholder_questions"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    question = Column(Text, nullable=False)
    purpose = Column(Text)
    target_role = Column(String(100))
    answer = Column(Text, nullable=True)
    answered_by = Column(String(255), nullable=True)
    answered_at = Column(DateTime, nullable=True)
    is_generated = Column(Boolean, default=True)  # True if AI-generated, False if manual
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="stakeholder_questions")


# ─── Research Citations ─────────────────────────────────────

# NOTE: ResearchCitation model removed — citations now live in agent output JSON
# (sources_cited field). The research_citations table may still exist in DBs
# but is no longer used or populated.


# ─── Output Documents ──────────────────────────────────────

class OutputDocument(Base):
    __tablename__ = "output_documents"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    crew_run_id = Column(Integer, ForeignKey("crew_runs.id"), nullable=True)
    doc_type = Column(String(50), nullable=False)  # marketing_plan, stakeholder_questions, executive_summary
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(255), nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="output_documents")
