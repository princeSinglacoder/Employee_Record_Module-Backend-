from app.database.employeeDB import Repository
from app.schemas.employee import Employee, TempEmployee, UpdateEmployee
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.config import get_db

class Employee_Service:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = Repository(db)

    def checkExist(self, userName: str) -> bool:
        employee = self.repo.getEmployeeIndividual(userName)
        return employee is not None

    def create(self, employee: Employee):
        # Check if department exists
        department = self.repo.getDepartmentIndividual(employee.departId)
        if not department:
            raise HTTPException(status_code=404, detail='Department does not exist')

        return self.repo.setInEmployee(employee)

    def get(self, userName: str):
        employee = self.repo.getEmployeeIndividual(userName)
        if not employee:
            raise HTTPException(status_code=404, detail='Employee does not exist')

        return employee

    def get_all(self):
        return self.repo.getEmployee()

    def update(self, userName: str, employeeUpdate: UpdateEmployee):
        # Check if employee exists
        if not self.checkExist(userName):
            raise HTTPException(status_code=404, detail='Employee not found')

        return self.repo.updateInEmployee(userName, employeeUpdate)

    def delete(self, userName: str):
        if not self.checkExist(userName):
            raise HTTPException(status_code=404, detail='Employee not found')

        return self.repo.deleteInEmployee(userName)