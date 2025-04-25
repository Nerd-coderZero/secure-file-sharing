# app/utils/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from itsdangerous import URLSafeTimedSerializer
from cryptography.fernet import Fernet
from app.config import settings
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# For password hashing
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# For email verification tokens
def create_verification_token(data: dict) -> str:
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    return s.dumps(data)

def verify_token(token: str, expiration=3600) -> dict:
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    return s.loads(token, max_age=expiration)

# For secure download links
key = Fernet.generate_key() if not hasattr(settings, 'FERNET_KEY') else settings.FERNET_KEY
fernet = Fernet(key)

def create_download_token(data: dict) -> str:
    # Token valid for 1 hour
    payload = {
        **data,
        "exp": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    json_data = json.dumps(payload).encode()
    return fernet.encrypt(json_data).decode()

def verify_download_token(token: str) -> dict:
    try:
        decrypted_data = fernet.decrypt(token.encode()).decode()
        payload = json.loads(decrypted_data)
        
        # Check expiration
        exp = datetime.fromisoformat(payload["exp"].replace("Z", "+00:00"))
        if datetime.utcnow() > exp:
            raise ValueError("Expired token")
        
        return payload
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")