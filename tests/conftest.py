import sys
from pathlib import Path


STARTER_DIR = Path(__file__).resolve().parents[1] / "starter"
sys.path.insert(0, str(STARTER_DIR))
