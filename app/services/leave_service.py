from app.schemas.leave import Leave, EmployeeLeaveRequest, UpdateEmployeeLeave
from app.database.leaveDB import LeaveDB
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config import get_db
import uuid
from datetime import datetime

class LeaveService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = LeaveDB(db)

    def create(self, leave_request: EmployeeLeaveRequest, userName: str):
        leave_id = str(uuid.uuid4())

        # Convert string dates to date objects
        try:
            start_date = datetime.strptime(leave_request.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(leave_request.end_date, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        leave = Leave(
            leave_id=leave_id,
            userName=userName,
            Leave_type=leave_request.Leave_type,
            start_date=leave_request.start_date,
            end_date=leave_request.end_date,
            reason=leave_request.reason,
            status='pending'
        )

        result = self.db.add_Leave(leave)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return {"message": "Leave applied successfully", "leave_id": leave_id}

    def get(self, leave_id: str) -> Leave:
        leave = self.db.get_Leave(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave not found")
        return leave

    def get_user_leaves(self, userName: str):
        return self.db.get_leaves_by_user(userName)

    def get_all_leaves(self):
        return self.db.get_all_leaves()

    def update(self, leave_id: str, leaveUpdate: UpdateEmployeeLeave):
        leave = self.db.get_Leave(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave not found")

        if leave.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending leave can be updated")

        result = self.db.update_Leave(leave_id, leaveUpdate)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result

    def update_status(self, leave_id: str, new_status: str, admin_username: str):
        """Admin function to approve/reject leave"""
        if new_status not in ['approved', 'rejected']:
            raise HTTPException(status_code=400, detail="Invalid status")

        leave = self.db.get_Leave(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave not found")

        update_data = UpdateEmployeeLeave(status=new_status)
        result = self.db.update_Leave(leave_id, update_data)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result

    def delete(self, leave_id: str):
        leave = self.db.get_Leave(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave not found")

        if leave.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending leave can be deleted")

        result = self.db.delete_leave(leave_id)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
