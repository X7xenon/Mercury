import sys
from pathlib import Path

# Add root directory to sys.path so server, bot_engine, database can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from server import app

# Export handler for serverless compatibility
try:
    from mangum import Mangum
    handler = Mangum(app)
except Exception:
    handler = app
