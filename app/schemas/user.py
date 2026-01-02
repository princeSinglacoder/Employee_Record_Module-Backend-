from pydantic import BaseModel, Field
from typing import Literal, Annotated

    
# login ke time data

class TempUserLogIn(BaseModel):
    userName: str
    password: str
    
class UserLogIn(TempUserLogIn):
    role: str  = 'employee'