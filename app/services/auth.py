from datetime import datetime, timedelta
import jwt

SECRET_KEY  = 'supersecret'
ALGORITHM = 'HS256'

# Create JWT after login
def create_jwt(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(minutes=60)
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Verify JWT token
def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
