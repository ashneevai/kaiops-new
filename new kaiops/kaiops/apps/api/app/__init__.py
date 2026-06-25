import sys
from pathlib import Path

# Make monorepo root importable so domain modules under /services are available.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))
