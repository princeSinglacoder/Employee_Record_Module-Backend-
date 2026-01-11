from fastapi import APIRouter, HTTPException, Response, Request, status
from app.schemas.user import LogIn
from app.database.user_repo import UserRepository
from app.utils.jwt import create_access_token, get_current_user

router = APIRouter(prefix="/auth")

@router.post("/login")
def login(login_data: LogIn, response: Response):
    user = UserRepository.get_user(login_data.userName)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "userName": user.userName,
        "role": user.role
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to False for localhost HTTP
        samesite="lax",
        path="/"  # Make cookie available for all paths
    )

    return {
        "message": "Login successfully",
        "userName": user.userName,
        "role": user.role,
        "token": token  # Also return token for frontend to store
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successfully"}

@router.get("/me")
def get_current_user_info(request: Request):
    current_user = get_current_user(request)
    return {
        "userName": current_user["userName"],
        "role": current_user["role"]
    }