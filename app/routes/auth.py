from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import LogIn
from app.database.user_repo import UserRepository
from app.utils.jwt import create_access_token

router =  APIRouter(prefix='/auth')


@router.post('/login')
def login(login_data: LogIn):

    username = login_data.userName
    password = login_data.password

    db_user = UserRepository.get_user(username)

    if not db_user:
        raise HTTPException(status_code=404, detail='User Not Found')

    if db_user.password != password:
        raise HTTPException(status_code=401, detail='Password not match')

    token = create_access_token({
        'userName': db_user.userName,
        'role': db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
