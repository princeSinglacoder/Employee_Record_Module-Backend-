from fastapi import APIRouter, HTTPException,Depends,status
from app.schemas.leave import EmployeeLeaveRequest
from app.services.leave_service import Leave, LeaveService
from app.database.leaveDB import LeaveDB
from app.utils.jwt import get_current_user
import uuid

router  = APIRouter(prefix='/leave')

service = LeaveService()

@router.get('/')    
def get_all_leaves(current_user=Depends(get_current_user)):

    if current_user['role']!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only admin can access all leaves')
    return LeaveDB.get_all_leaves()


@router.get('/{leave_id}')
def get_Leave(leave_id: str, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)

    if current_user['role'] == 'employee' and leave.userName != current_user['userName']:
        raise HTTPException(status_code=403, detail="You can view only your leave")

    return leave


@router.post('/')
def apply_Leave(employeeLeaveRequest:EmployeeLeaveRequest,current_user=Depends(get_current_user)):
    if current_user['role']!='employee':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only employee can apply for leave')
    
    currentEmployee = Leave(**employeeLeaveRequest.dict(),leave_id= str(uuid.uuid4()),userName=current_user['userName'],status='pending')
    # Logic to apply for leave
    return service.create(currentEmployee.leave_id,currentEmployee)


@router.put('/{leave_id}')
def update_leave(leave_id: str, leave_update: EmployeeLeaveRequest, current_user=Depends(get_current_user)):
    if current_user['role'] != 'employee':
        raise HTTPException(status_code=403, detail='Only employee can update leave')

    leave = service.get(leave_id)

    if leave.userName != current_user['userName']:
        raise HTTPException(status_code=403, detail='You can update only your leave')

    return service.update(leave_id, leave_update)


@router.delete('/{leave_id}')
def delete_leave(leave_id: str, current_user=Depends(get_current_user)):
    leave = service.get(leave_id)

    if current_user['role'] == 'employee' and leave.userName != current_user['userName']:
        raise HTTPException(status_code=403, detail="You can delete only your leave")

    if leave.status == 'pending':
        if current_user['role'] != 'employee':
            raise HTTPException(status_code=403, detail='Only employee can delete pending leave')
    else:
        if current_user['role'] != 'admin':
            raise HTTPException(status_code=403, detail='Only admin can delete approved leave')

    return service.delete(leave_id)

    
@router.put('/approve/{leave_id}')
def approve_leave(leave_id:str,current_user=Depends(get_current_user)):
    
    leave  = service.get(leave_id)
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Leave not found')
    
    if current_user['role']!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only admin can approve leave')
    
    leave_update = Leave(**leave)
    leave_update.status = 'approved'
    return service.update(leave_id,leave_update)

@router.put('/reject/{leave_id}')
def reject_leave(leave_id:str,current_user=Depends(get_current_user)):

    leave  = service.get(leave_id)
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Leave not found')
    
    if current_user['role']!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only admin can reject leave')
    
    leave_update = Leave(**leave)
    leave_update.status = 'rejected'
    return service.update(leave_id,leave_update)
