from pydantic import BaseModel, Field
from typing import Literal, Annotated

    
# login ke time data

class UserLogIn(BaseModel):
    userName: str
    password: str
    

# This is hidden
class EmployeeUserLogIn(UserLogIn):
    role: str  = 'employee'