from pydantic import BaseModel, Field
from typing import Literal, Annotated

class EmployeeLeaveRequest(BaseModel):
    Leave_type: Literal['sick', 'casual', 'earned']
    start_date: str
    end_date: str
    reason: Annotated[str, Field(min_length =10, max_length = 300)]

class Leave(EmployeeLeaveRequest):
    leave_id: str
    userName: str
    status: Literal['pending', 'approved', 'rejected'] = 'pending'
