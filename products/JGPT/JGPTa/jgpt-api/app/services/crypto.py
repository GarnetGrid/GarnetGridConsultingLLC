from cryptography.fernet import Fernet
import os
import base64


# Ensure we have a valid Fernet key
# If SECRET_KEY is not 32 bytes base64 encoded, we derive one or use a fallback for dev
# In production, this should be a strict env var
def get_fernet_key() -> bytes:
    key = os.getenv("ENCRYPTION_KEY")
    if key:
        return key.encode()
    
    # Fallback: Derive from SECRET_KEY (not ideal for high security but works for phase 1)
    # Fernet requires a 32-byte url-safe base64 encoded key
    secret = os.getenv("SECRET_KEY", "jgpt_super_secret_key_change_me_in_prod")
    # Pad or truncate to 32 bytes then base64 encode
    # Creating a deterministic key from secret for dev convenience
    # In real prod, generate with Fernet.generate_key()
    import hashlib
    m = hashlib.sha256()
    m.update(secret.encode())
    return base64.urlsafe_b64encode(m.digest())

cipher_suite = Fernet(get_fernet_key())

def encrypt_string(plain_text: str) -> str:
    if not plain_text:
        return ""
    return cipher_suite.encrypt(plain_text.encode()).decode()

def decrypt_string(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    try:
        return cipher_suite.decrypt(cipher_text.encode()).decode()
    except Exception:
        # If key changed or currupt, return empty or raise
        return "[Error: Decryption Failed]"
