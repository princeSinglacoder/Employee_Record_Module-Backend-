from pydantic import BaseModel,Field, computed_field
from typing import Annotated, Literal, Optional
import uuid

class TempEmployee(BaseModel):
    empName: Annotated[str,Field(..., description='Name of the Employee')]
    empAge: Annotated[int,Field(..., gt=0,lt=120, description='Age of the Employee')]
    empSalary: Annotated[float,Field(..., gt=0, description='Salary of the Employee')]
    departId: Annotated[str,Field(..., description='DepartId of the Employee')]

class Employee(TempEmployee): 
    #empUserName,empPassword
    empUserName: str
    empPassword: int = 123456
