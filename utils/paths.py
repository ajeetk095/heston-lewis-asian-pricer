"""Project paths that do not depend on the current working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "option_data.xlsx"
RESULTS_FILE = ROOT / "results" / "gwp1_results.json"
REPORT_DIR = ROOT / "reports"
NOTEBOOK_DIR = ROOT / "notebooks"
DOC_DIR = ROOT / "documentation"
