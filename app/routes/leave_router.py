from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.leave import EmployeeLeaveRequest, Leave
from app.services.leave_service import LeaveService
from app.database.leaveDB import LeaveDB
from app.utils.jwt import get_current_user
import uuid

router = APIRouter(prefix="/leave")
service = LeaveService()

@router.get("/")
def get_all_leaves(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can access all leaves")
    return LeaveDB.get_all_leaves()

@router.get("/{leave_id}")
def get_leave(leave_id: str, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)
    if current_user["role"] != "admin" and leave.userName != current_user["userName"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own leave")
    return leave

@router.post("/")
def apply_leave(employeeLeaveRequest: EmployeeLeaveRequest, current_user=Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employee can apply for leave")

    leave_obj = Leave(
        **employeeLeaveRequest.dict(),
        leave_id=str(uuid.uuid4()),
        userName=current_user["userName"],
        status="pending"
    )
    return service.create(leave_obj.leave_id, leave_obj)

@router.put("/{leave_id}")
def update_leave(leave_id: str, leave_update: EmployeeLeaveRequest, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)
    if leave.userName != current_user["userName"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own leave")

    return service.update(leave_id, leave_update)

@router.delete("/{leave_id}")
def delete_leave(leave_id: str, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)
    if leave.userName != current_user["userName"] and current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can delete only your leave or admin can delete")

    return service.delete(leave_id)

@router.put("/approve/{leave_id}")
def approve_leave(leave_id: str, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can approve leave")

    leave.status = "approved"
    return service.update(leave_id, leave)

@router.put("/reject/{leave_id}")
def reject_leave(leave_id: str, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can reject leave")

    leave.status = "rejected"
    return service.update(leave_id, leave)
