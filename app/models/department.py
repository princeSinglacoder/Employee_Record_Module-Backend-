from sqlalchemy import Column, Integer, String
from app.config import Base

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    departId = Column(String, unique=True, nullable=False)
    departName = Column(String, nullable=False)