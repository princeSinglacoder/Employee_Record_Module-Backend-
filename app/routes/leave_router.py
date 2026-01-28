from fastapi import APIRouter, HTTPException, Depends, status, Request
from app.schemas.leave import EmployeeLeaveRequest, Leave, UpdateEmployeeLeave
from app.services.leave_service import LeaveService
from app.services.employee_service import Employee_Service
from app.database.leaveDB import LeaveDB
from app.utils.jwt import get_current_user
from sqlalchemy.orm import Session
from app.config import get_db
import uuid
from app.websocket.notification_ws import manager

router = APIRouter(prefix="/leave")

@router.get("/")
def get_all_leaves(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can access all leaves")

    leave_db = LeaveDB(db)
    return leave_db.get_all_leaves()

@router.get("/my")
def get_my_leaves(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    leave_service = LeaveService(db)
    return leave_service.get_user_leaves(current_user["userName"])

@router.get("/{leave_id}")
def get_leave(leave_id: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    leave_service = LeaveService(db)

    leave = leave_service.get(leave_id)
    if current_user['role'] == 'admin' or current_user['userName'] == leave.userName:
        return leave
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own leave")

@router.post("/")
def apply_leave(employeeLeaveRequest: EmployeeLeaveRequest, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user["role"] != "employee":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employee can apply for leave")

    leave_service = LeaveService(db)
    return leave_service.create(employeeLeaveRequest, current_user["userName"])

@router.put("/{leave_id}")
def update_leave(leave_id: str, leave_update: UpdateEmployeeLeave, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    leave_service = LeaveService(db)

    leave = leave_service.get(leave_id)

    if current_user['role'] == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin cannot update employee leave')

    if leave.userName != current_user["userName"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own leave")

    return leave_service.update(leave_id, leave_update)

@router.delete("/{leave_id}")
def delete_leave(leave_id: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    leave_service = LeaveService(db)

    leave = leave_service.get(leave_id)

    if current_user['role'] == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin cannot delete employee leave")

    if leave.userName != current_user['userName']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own leave")

    return leave_service.delete(leave_id)

@router.put("/approve/{leave_id}")
async def approve_leave(leave_id: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can approve leave")

    leave_service = LeaveService(db)
    
    # Get employee details for notification
    leave_obj = leave_service.get(leave_id)
    emp_service = Employee_Service(db)
    employee = emp_service.get(leave_obj.userName)
    
    result = leave_service.update_status(leave_id, "approved", current_user["userName"])

    # -------- STEP 5: Notify employee after approval --------
    try:
        await manager.notify_employee(
            employee.id,
            {
                "type": "LEAVE_APPROVED",
                "message": "Your leave request has been approved ✅"
            }
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

    return result

@router.put("/reject/{leave_id}")
async def reject_leave(leave_id: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can reject leave")

    leave_service = LeaveService(db)
    
    # Get employee details for notification
    leave_obj = leave_service.get(leave_id)
    emp_service = Employee_Service(db)
    employee = emp_service.get(leave_obj.userName)
    
    result = leave_service.update_status(leave_id, "rejected", current_user["userName"])

    # -------- STEP 5: Notify employee after rejection --------
    try:
        await manager.notify_employee(
            employee.id,
            {
                "type": "LEAVE_REJECTED",
                "message": "Your leave request has been rejected ❌"
            }
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

    return result
