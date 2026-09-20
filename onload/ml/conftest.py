import sys
from pathlib import Path

# lets every lesson's test do `from _load import load`
sys.path.insert(0, str(Path(__file__).parent))
