import sys
from pathlib import Path

# Add docker/ to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'docker'))
# Add agents/ parent to path so 'from venture_generator.agent import ...' works
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
