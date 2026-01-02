from fastapi import APIRouter, HTTPException
from app.schemas.user import UserLogIn,TempUserLogIn
from app.database.user_repo import UserRepository
from app.utils.jwt import create_access_token

router =  APIRouter(prefix='/auth')

@router.post('/login')
def login(tempUserLogIn:TempUserLogIn):
    db_user = UserRepository.get_user(tempUserLogIn.userName)
    
    if not db_user:
        raise HTTPException(status_code=404, detail='User Not Found')
    
    if db_user.password != tempUserLogIn.password:
        raise HTTPException(status_code=401, detail='Password not match')
    
    token = create_access_token({
        'sub': db_user.userName,
        'role': db_user.role
    })
    
    # After login we send create a token and send it as response
    return {
        "access_token": token,
        "token_type": "bearer"
    }