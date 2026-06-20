import sys
from pathlib import Path

# Add docker/ to path so shared module is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'docker'))
# Add this server's directory to path so server module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
