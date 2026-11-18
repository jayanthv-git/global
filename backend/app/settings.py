import os
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'config'
RUNTIME = ROOT / '.runtime'
RUNTIME.mkdir(mode=0o700, exist_ok=True)
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{RUNTIME / "wellbeing.db"}')
def config(name):
    return yaml.safe_load((CONFIG / name).read_text())
