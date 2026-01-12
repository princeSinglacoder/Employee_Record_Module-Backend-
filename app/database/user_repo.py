from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import EmployeeUserLogIn
from typing import Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_user(self, user: EmployeeUserLogIn) -> bool:
        # Check if user already exists
        existing = self.db.query(UserModel).filter(UserModel.userName == user.userName).first()
        if existing:
            return False

        db_user = UserModel(
            userName=user.userName,
            password=user.password,
            role=user.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return True

    def get_user(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.userName == username).first()

    def get_all_users(self):
        return self.db.query(UserModel).all()

    def update_user_role(self, username: str, new_role: str) -> dict:
        db_user = self.db.query(UserModel).filter(UserModel.userName == username).first()
        if not db_user:
            return {'error': 'User not found'}

        db_user.role = new_role
        self.db.commit()
        return {'message': 'User role updated successfully'}

    def delete_user(self, username: str) -> dict:
        db_user = self.db.query(UserModel).filter(UserModel.userName == username).first()
        if not db_user:
            return {'error': 'User not found'}

        self.db.delete(db_user)
        self.db.commit()
        return {'message': 'User deleted successfully'}