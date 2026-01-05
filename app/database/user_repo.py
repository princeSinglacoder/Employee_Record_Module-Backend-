from typing import Dict
from app.schemas.user import UserLogIn, EmployeeUserLogIn

# In this db we generally store the user information

class UserRepository:
    __users = {}

    __users['Prince349'] = EmployeeUserLogIn(userName='Prince349', password='singla123', role='admin')
    
    @classmethod
    def add_user(cls,user:UserLogIn):
        if user.userName in cls.__users:
            return False
        cls.__users[user.userName]=user
        return True
    
    @classmethod
    def get_user(cls,username:str):
        return cls.__users.get(username)