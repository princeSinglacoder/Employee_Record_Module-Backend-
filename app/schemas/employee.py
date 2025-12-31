from pydantic import BaseModel,Field, computed_field
from typing import Annotated, Literal, Optional


class Employee(BaseModel):
    empId: Annotated[str,Field(..., description='Id of the Employee',examples=['2088'])]
    empName: Annotated[str,Field(..., description='Name of the Employee')]
    empAge: Annotated[int,Field(..., gt=0,lt=120, description='Age of the Employee')]
    empSalary: Annotated[float,Field(..., gt=0, description='Salary of the Employee')]
    departId: Annotated[str,Field(..., description='DepartId of the Employee')]

# create new pydantic model of employee for updation 
class EmployeeUpdate(BaseModel):
    empName: Annotated[Optional[str], Field(default= None)]
    empAge: Annotated[Optional[int], Field(default= None, gt=0, lt=120)]
    empSalary: Annotated[Optional[float], Field(default=None, gt=0)]
    empDepartId: Annotated[Optional[str], Field(default=None)]