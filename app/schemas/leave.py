from pydantic import BaseModel, Field
from typing import Literal, Annotated, Optional

# Employee input
class EmployeeLeaveRequest(BaseModel):
    Leave_type: Literal['sick', 'casual', 'earned']
    start_date: str
    end_date: str
    reason: Annotated[str, Field(min_length=10, max_length=300)]


class UpdateEmployeeLeave(BaseModel):
    Leave_type: Annotated[Optional[Literal['sick', 'casual', 'earned']], Field(default=None)]
    start_date: Annotated[Optional[str], Field(default=None)]
    end_date: Annotated[Optional[str], Field(default=None)]
    reason: Annotated[Optional[str], Field(default=None)]

# Admin / internal object
class Leave(EmployeeLeaveRequest):
    leave_id: str
    userName: str
    status: Literal['pending', 'approved', 'rejected'] = 'pending'
