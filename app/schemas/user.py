from pydantic import BaseModel, Field
from typing import Literal, Annotated

# SignUp ke time ka data

class TempUserCreate(BaseModel):
    userName: Annotated[str, Field(..., description='Name of User')]
    password: str

class UserCreate(TempUserCreate):
    role: str = 'user'
    

# login ke time data
class UserLogIn(BaseModel):
    usereName: str
    password: str