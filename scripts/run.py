"""One-command local launcher. Network needed only for initial dependency setup."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if sys.version_info<(3,11): raise SystemExit('Python 3.11 or newer is required.')
python=ROOT/'.venv/bin/python'
if not python.exists():
    subprocess.run([sys.executable,'-m','venv',str(ROOT/'.venv')],check=True)
check=subprocess.run([str(python),'-c','import fastapi,uvicorn,sqlalchemy,cryptography,yaml'],capture_output=True)
if check.returncode:
    subprocess.run([str(python),'-m','pip','install','-r','backend/requirements.txt'],check=True)
if not (ROOT/'frontend/node_modules/vite').exists():
    subprocess.run(['npm','ci','--prefix','frontend','--ignore-scripts'],check=True)
paths=sorted([*(ROOT/'frontend/src').rglob('*'),*(ROOT/'frontend/public').rglob('*'),*(ROOT/'frontend/scripts').rglob('*'),ROOT/'frontend/index.html',ROOT/'frontend/package-lock.json',ROOT/'frontend/vite.config.js'])
digest=hashlib.sha256(b''.join(p.read_bytes() for p in paths if p.is_file())).hexdigest()
stamp=ROOT/'.runtime/frontend.sha256';stamp.parent.mkdir(mode=0o700,exist_ok=True)
if not stamp.exists() or stamp.read_text()!=digest or not (ROOT/'frontend/dist/index.html').exists():
    subprocess.run(['npm','--prefix','frontend','run','build'],check=True)
    stamp.write_text(digest)
port=os.getenv('PORT','8000')
print(f'\nSaha local synthetic demo: http://127.0.0.1:{port}\nNo real patients or clinicians. Press Ctrl+C to stop.\n',flush=True)
os.execv(str(python),[str(python),'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port',port])
