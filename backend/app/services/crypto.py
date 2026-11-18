import json
import os
from cryptography.fernet import Fernet
from ..settings import RUNTIME

def cipher():
    key = os.getenv('FIELD_ENCRYPTION_KEY')
    if not key:
        path = RUNTIME / 'field.key'
        if not path.exists():
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, 'wb') as f:
                    f.write(Fernet.generate_key())
            except FileExistsError:
                pass
        key = path.read_bytes()
    return Fernet(key)
def encrypt(value):
    return cipher().encrypt(json.dumps(value).encode()).decode()
def decrypt(value):
    return json.loads(cipher().decrypt(value.encode()))
