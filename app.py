"""Root entry point for Streamlit Community Cloud and Hugging Face Spaces."""
import runpy
import sys
from pathlib import Path

FRONTEND = str(Path(__file__).resolve().parent / "frontend")
if FRONTEND not in sys.path:
    sys.path.insert(0, FRONTEND)

runpy.run_path(str(Path(FRONTEND) / "app.py"), run_name="__main__")
