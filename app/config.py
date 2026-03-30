import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'idideration.db'}")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-production")
NARRALYTICA_API_URL = os.getenv("NARRALYTICA_API_URL", "http://localhost:8005/api")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8006"))

PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(exist_ok=True)

# Gemini model configuration per agent
AGENT_MODELS = {
    "research_agent": "gemini-2.5-flash",
    "intake_analyst": "gemini-2.5-flash",
    "behavioral_scientist": "gemini-2.5-pro",
    "psychometrics_expert": "gemini-2.5-pro",
    "competitive_intelligence": "gemini-2.5-flash",
    "social_strategist": "gemini-2.5-flash",
    "chief_strategist": "gemini-2.5-pro",
    "creative_director": "gemini-2.5-pro",
    "stakeholder_agent": "gemini-2.5-flash",
}

AGENT_TEMPERATURE = 0.7
AGENT_MAX_TOKENS = 65536
