"""Helper to load prompt modules from the prompts/ directory."""
import importlib.util
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"


def load_prompt_module(filename: str):
    """Load a prompt module by filename (without .py extension)."""
    path = PROMPTS_DIR / f"{filename}.py"
    spec = importlib.util.spec_from_file_location(f"prompt_{filename}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
