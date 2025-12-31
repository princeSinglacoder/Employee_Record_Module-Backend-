from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional

class Department(BaseModel):
    departId: Annotated[str, Field(..., description="Id of the Department")]
    departName: Annotated[str, Field(..., description="Name of the Department")]

# create new pydantic model of Department for u pdation 
class DepartmentUpdate(BaseModel):
    departName: Annotated[Optional[str], Field(default= None)]