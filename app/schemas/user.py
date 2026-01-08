from pydantic import BaseModel, Field
from typing import Literal, Annotated

    
# login ke time data
class LogIn(BaseModel):
    userName: str
    password: str

# This is hidden
class EmployeeUserLogIn(BaseModel):
    userName: str
    password: str
    role: str  = 'employee'