from jose import jwt, JWTError
from datetime import datetime,timedelta
from fastapi import Request,HTTPException,status

SECRET_KEY = 'SECRET123'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)


def get_current_user(request:Request):
    # Try to get token from cookie first
    token = request.cookies.get('access_token')
    
    # Fallback: Try to get from Authorization header
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload