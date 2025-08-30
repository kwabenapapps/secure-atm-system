from __future__ import annotations
import os
from cryptography.fernet import Fernet

KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")

def generate_key(path: str = KEY_FILE) -> bytes:
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

def load_key(path: str = KEY_FILE) -> bytes:
    if not os.path.exists(path):
        return generate_key(path)
    with open(path, "rb") as f:
        return f.read()

def get_cipher(path: str = KEY_FILE) -> Fernet:
    return Fernet(load_key(path))
