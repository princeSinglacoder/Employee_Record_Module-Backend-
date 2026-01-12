from fastapi import HTTPException, Depends
from app.schemas.department import Department, DepartmentUpdate
from app.database.employeeDB import Repository
from sqlalchemy.orm import Session
from app.config import get_db

class Department_Service:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = Repository(db)

    def create(self, department: Department):
        # Check if department exists
        existing = self.repo.getDepartmentIndividual(department.departId)
        if existing:
            raise HTTPException(status_code=400, detail='Department already exists')

        return self.repo.setInDepart(department)

    def get(self, departId: str):
        department = self.repo.getDepartmentIndividual(departId)
        if not department:
            raise HTTPException(status_code=404, detail='Department does not exist')

        return department

    def get_all(self):
        return self.repo.getDepartment()

    def update(self, departId: str, departmentUpdate: DepartmentUpdate):
        # Check if department exists
        if not self.repo.getDepartmentIndividual(departId):
            raise HTTPException(status_code=404, detail='Department not found')

        return self.repo.updateInDepartment(departId, departmentUpdate)

    def delete(self, departId: str):
        if not self.repo.getDepartmentIndividual(departId):
            raise HTTPException(status_code=404, detail='Department not found')

        return self.repo.deleteInDepartment(departId)