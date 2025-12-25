import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

def get_encryption_key():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate one for first-time use, but practically it must be in env
        raise ValueError("ENCRYPTION_KEY not set in environment")
    return key.encode()

def encrypt_value(value: str) -> str:
    if not value: return ""
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_value(token: str) -> str:
    if not token: return ""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        return f.decrypt(token.encode()).decode()
    except Exception as e:
        # Fallback: maybe it's not encrypted?
        # print(f"Decryption failed, assuming plaintext: {e}")
        return token

def get_secret(key_name: str, default=None) -> str:
    val = os.getenv(key_name, default)
    if not val:
        return default
    
    # Heuristic: Fernet tokens start with gAAAA...
    if val.startswith("gAAAA"):
        try:
            return decrypt_value(val)
        except:
            return val
    return val
