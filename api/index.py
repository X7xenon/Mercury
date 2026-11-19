import sys
from pathlib import Path

# Add parent directory to sys.path so server, bot_engine, database can be imported cleanly
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from server import app
