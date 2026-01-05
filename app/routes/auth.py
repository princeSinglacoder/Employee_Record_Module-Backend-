from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.database.user_repo import UserRepository
from app.utils.jwt import create_access_token

router =  APIRouter(prefix='/auth')


@router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Swagger UI and OAuth2 clients send credentials as form data
    username = form_data.username
    password = form_data.password

    db_user = UserRepository.get_user(username)

    if not db_user:
        raise HTTPException(status_code=404, detail='User Not Found')

    if db_user.password != password:
        raise HTTPException(status_code=401, detail='Password not match')

    token = create_access_token({
        'sub': db_user.userName,
        'role': db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
