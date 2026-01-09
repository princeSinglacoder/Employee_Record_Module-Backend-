from fastapi import APIRouter, HTTPException, Depends, status, Request
from app.schemas.leave import EmployeeLeaveRequest, Leave, UpdateEmployeeLeave
from app.services.leave_service import LeaveService
from app.database.leaveDB import LeaveDB
from app.utils.jwt import get_current_user
import uuid

router = APIRouter(prefix="/leave")
service = LeaveService()

@router.get("/")
def get_all_leaves(request: Request):
    current_user = get_current_user(request)

    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can access all leaves")
    return LeaveDB.get_all_leaves()

@router.get("/my")
def get_my_leaves(request: Request):
    current_user = get_current_user(request)
    all_leaves = LeaveDB.get_all_leaves()
    # Filter leaves for current user
    my_leaves = {leave_id: leave for leave_id, leave in all_leaves.items() if leave.userName == current_user["userName"]}
    return my_leaves

@router.get("/{leave_id}")
def get_leave(leave_id: str, request: Request):
    current_user = get_current_user(request)

    leave  = service.get(leave_id)
    if current_user['role']=='admin' or current_user['userName']==leave.userName:
        return leave
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own leave")

@router.post("/")
def apply_leave(employeeLeaveRequest: EmployeeLeaveRequest, request: Request):
    current_user = get_current_user(request)
    if current_user["role"] != "employee":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employee can apply for leave")

    leave_obj = Leave(
        **employeeLeaveRequest.dict(),
        leave_id=str(uuid.uuid4()),
        userName=current_user["userName"],
        status="pending"
    )
    service.create(leave_obj.leave_id, leave_obj)
    return {
        "message": "Leave applied successfully",
        "leave_id": leave_obj.leave_id
    }

@router.put("/{leave_id}")
def update_leave(leave_id: str, leave_update: UpdateEmployeeLeave, request: Request):
    current_user = get_current_user(request)
    leave = service.get(leave_id)

    if current_user['role'] == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Admin cannot update employee leave')
    
    if leave.userName != current_user["userName"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own leave")

    service.update(leave_id, leave_update)
    return {'message': 'Leave updated successfully'}

@router.delete("/{leave_id}")
def delete_leave(leave_id: str, request: Request):
    current_user = get_current_user(request)
    leave = service.get(leave_id)
    
    if current_user['role']=='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin cannot delete employee leave")
    
    if leave.userName != current_user['userName']:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="You can only delete your own leave")
    
    service.delete(leave_id)
    return {'message': 'Leave deleted successfully'}

@router.put("/approve/{leave_id}")
def approve_leave(leave_id: str, request: Request):
    current_user = get_current_user(request)
    leave = service.get(leave_id)

    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can approve leave")

    leave.status = "approved"
    service.create(leave_id, leave)
    return {'message': 'Leave approved successfully'}

@router.put("/reject/{leave_id}")
def reject_leave(leave_id: str, request: Request):
    current_user = get_current_user(request)
    leave = service.get(leave_id)

    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can reject leave")

    leave.status = "rejected"
    service.create(leave_id, leave)
    return {'message': 'Leave rejected'}
