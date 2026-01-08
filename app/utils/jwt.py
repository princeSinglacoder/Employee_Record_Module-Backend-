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
    auth_header = request.headers.get('Authorization')   # header se token nikala
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    scheme, token = auth_header.split(" ")
    if scheme != "Bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication scheme")
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload