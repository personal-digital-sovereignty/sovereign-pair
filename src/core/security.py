import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

logger = logging.getLogger(__name__)

# Cache of the AESGCM instance
_aesgcm = None

def init_security():
    global _aesgcm
    if _aesgcm is not None:
        return

    # KEK (Key Encryption Key) must be 32 bytes for AES-256-GCM
    key_str = os.environ.get("SOVEREIGN_MASTER_KEK", "").strip()
    
    if not key_str:
        logger.warning("SOVEREIGN_MASTER_KEK not set. Using ephemeral dev key. DO NOT USE IN PRODUCTION.")
        key = b"0" * 32  # 32 bytes of zeros for development fallback
    else:
        try:
            if len(key_str) == 64:  # Hex format
                key = bytes.fromhex(key_str)
            else:  # Base64 format
                key = base64.b64decode(key_str)
                
            if len(key) != 32:
                raise ValueError("SOVEREIGN_MASTER_KEK must be exactly 32 bytes (256 bits).")
                
            # CISO GOTCHA: APM Leakage Prevention. 
            # Destroy the environment variable from memory to prevent APM/Crash Dumps from catching it.
            if "SOVEREIGN_MASTER_KEK" in os.environ:
                del os.environ["SOVEREIGN_MASTER_KEK"]
                
        except Exception as e:
            logger.error(f"Invalid SOVEREIGN_MASTER_KEK format: {e}")
            raise

    _aesgcm = AESGCM(key)

def encrypt_value(plain_text: str) -> str:
    """Encrypts a string using AES-256-GCM and returns a base64 encoded payload."""
    if plain_text is None or not str(plain_text).strip():
        return plain_text

    init_security()
    
    nonce = os.urandom(12) # GCM standard nonce size
    cipher_text = _aesgcm.encrypt(nonce, plain_text.encode('utf-8'), None)
    
    # Store nonce + cipher_text together, base64 encoded
    payload = nonce + cipher_text
    return base64.b64encode(payload).decode('utf-8')

def decrypt_value(cipher_text_b64: str) -> str:
    """Decrypts a base64 encoded AES-256-GCM payload. Returns original if not valid format (legacy fallback)."""
    if cipher_text_b64 is None or not str(cipher_text_b64).strip():
        return cipher_text_b64

    init_security()

    try:
        data = base64.b64decode(cipher_text_b64)
        if len(data) < 28: # 12 bytes nonce + 16 bytes auth tag min
            # Return as is (legacy plaintext fallback)
            return cipher_text_b64
            
        nonce = data[:12]
        cipher_text = data[12:]
        plain_text = _aesgcm.decrypt(nonce, cipher_text, None)
        return plain_text.decode('utf-8')
    except (ValueError, InvalidTag, TypeError, base64.binascii.Error):
        # Failure to decode base64 or invalid MAC tag perfectly acts as legacy plaintext fallback
        return cipher_text_b64
