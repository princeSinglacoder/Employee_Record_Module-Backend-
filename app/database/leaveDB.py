from sqlalchemy.orm import Session
from app.models.leave import Leave as LeaveModel
from app.schemas.leave import Leave, UpdateEmployeeLeave
from typing import List, Optional
from datetime import datetime

class LeaveDB:
    def __init__(self, db: Session):
        self.db = db

    def add_Leave(self, leave: Leave) -> dict:
        # Check if leave with same leave_id already exists
        existing = self.db.query(LeaveModel).filter(LeaveModel.leave_id == leave.leave_id).first()
        if existing:
            return {'error': 'Leave with this ID already exists'}

        # Convert string dates to date objects
        try:
            start_date = datetime.strptime(leave.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(leave.end_date, '%Y-%m-%d').date()
        except ValueError:
            return {'error': 'Invalid date format. Use YYYY-MM-DD'}

        db_leave = LeaveModel(
            leave_id=leave.leave_id,
            userName=leave.userName,
            Leave_type=leave.Leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=leave.reason,
            status=leave.status
        )
        self.db.add(db_leave)
        self.db.commit()
        self.db.refresh(db_leave)
        return {'message': 'Leave applied successfully', 'id': db_leave.id}

    def get_Leave(self, leave_id: str) -> Optional[LeaveModel]:
        return self.db.query(LeaveModel).filter(LeaveModel.leave_id == leave_id).first()

    def get_all_leaves(self) -> List[LeaveModel]:
        return self.db.query(LeaveModel).all()

    def get_leaves_by_user(self, username: str) -> List[LeaveModel]:
        return self.db.query(LeaveModel).filter(LeaveModel.userName == username).all()

    def update_Leave(self, leave_id: str, leave_update: UpdateEmployeeLeave) -> dict:
        db_leave = self.db.query(LeaveModel).filter(LeaveModel.leave_id == leave_id).first()
        if not db_leave:
            return {'error': 'Leave not found'}

        update_data = leave_update.model_dump(exclude_unset=True)

        # Convert date strings if provided
        if 'start_date' in update_data and update_data['start_date']:
            try:
                update_data['start_date'] = datetime.strptime(update_data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid start_date format. Use YYYY-MM-DD'}

        if 'end_date' in update_data and update_data['end_date']:
            try:
                update_data['end_date'] = datetime.strptime(update_data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'Invalid end_date format. Use YYYY-MM-DD'}

        for field, value in update_data.items():
            setattr(db_leave, field, value)

        self.db.commit()
        return {'message': 'Leave updated successfully'}

    def delete_leave(self, leave_id: str) -> dict:
        db_leave = self.db.query(LeaveModel).filter(LeaveModel.leave_id == leave_id).first()
        if not db_leave:
            return {'error': 'Leave not found'}

        self.db.delete(db_leave)
        self.db.commit()
        return {'message': 'Leave deleted successfully'}
