# from sqlalchemy import Column, Integer, String, Float, DateTime
# from datetime import datetime
# from app.database.database import Base

# class Employee(Base):
#     __tablename__ = 'employees'

#     # 🔑 Primary Key (internal, never exposed)
#     id = Column(Integer, primary_key=True, index=True)

#     # Employee Details
#     empName = Column(String, nullable= False)
#     empAge = Column(Integer, nullable= False)
#     empSalary = Column(Float, nullable= False)
#     departId = Column(String, nullable= False)

#     # Login Credentials
#     userName = Column(String, unique=True, nullable= False)
#     password = Column(String, nullable= False)

#     # Role
#     role = Column(String, default='employee')
    
