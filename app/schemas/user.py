from pydantic import BaseModel, Field
from typing import Literal, Annotated

    
# login ke time data

# This is hidden
class EmployeeUserLogIn(BaseModel):
    userName: str
    password: str
    role: str  = 'employee'