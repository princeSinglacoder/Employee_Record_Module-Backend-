from sqlalchemy import Column, Integer, String, Date
from app.config import Base

class Leave(Base):
    __tablename__ = 'leaves'

    id = Column(Integer, primary_key=True, index=True)
    leave_id = Column(String, unique=True, nullable=False)
    userName = Column(String, nullable=False)
    Leave_type = Column(String, nullable=False)  # 'sick', 'casual', 'earned'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default='pending')  # 'pending', 'approved', 'rejected'