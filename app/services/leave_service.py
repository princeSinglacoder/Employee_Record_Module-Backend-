from app.schemas.leave import Leave, EmployeeLeaveRequest, UpdateEmployeeLeave
from app.database.leaveDB import LeaveDB
from fastapi import HTTPException, status

class LeaveService:
    def create(self, leave_id: str, leave: Leave):
        LeaveDB.add_Leave(leave_id, leave)

    def get(self, leave_id: str) -> Leave:
        leave = LeaveDB.get_Leave(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave not found")
        return leave

    def update(self, leave_id: str, leaveUpdate: UpdateEmployeeLeave):
        existLeave = LeaveDB.get_Leave(leave_id)

        if existLeave.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending leave can be updated")

        update_data = leaveUpdate.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(existLeave, key, value)

        LeaveDB.update_Leave(leave_id, existLeave)

    def delete(self, leave_id: str):

        if LeaveDB.get_Leave(leave_id).status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending leave can be deleted")
        LeaveDB.delete_leave(leave_id)
