from sqlalchemy.orm import Session
from app.models.employee import Employee as EmployeeModel
from app.models.department import Department as DepartmentModel
from app.schemas.employee import Employee, UpdateEmployee
from app.schemas.department import Department, DepartmentUpdate
from typing import List, Optional

class Repository:
    def __init__(self, db: Session):
        self.db = db

    # For Employee
    def setInEmployee(self, employee: Employee) -> dict:
        # Check if employee with same username already exists
        existing = self.db.query(EmployeeModel).filter(EmployeeModel.userName == employee.userName).first()
        if existing:
            return {'error': 'Employee with this username already exists'}

        db_employee = EmployeeModel(
            empName=employee.empName,
            empAge=employee.empAge,
            empSalary=employee.empSalary,
            departId=employee.departId,
            userName=employee.userName,
            password=employee.password,
            role='employee'  # Default role
        )
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        return {'message': "Employee added successfully", 'id': db_employee.id}

    def getEmployeeIndividual(self, username: str) -> Optional[EmployeeModel]:
        return self.db.query(EmployeeModel).filter(EmployeeModel.userName == username).first()

    def getEmployee(self) -> List[EmployeeModel]:
        return self.db.query(EmployeeModel).all()

    def updateInEmployee(self, username: str, employee_update: UpdateEmployee) -> dict:
        db_employee = self.db.query(EmployeeModel).filter(EmployeeModel.userName == username).first()
        if not db_employee:
            return {'error': 'Employee not found'}

        update_data = employee_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_employee, field, value)

        self.db.commit()
        return {'message': "Employee updated successfully"}

    def deleteInEmployee(self, username: str) -> dict:
        db_employee = self.db.query(EmployeeModel).filter(EmployeeModel.userName == username).first()
        if not db_employee:
            return {'error': 'Employee not found'}

        self.db.delete(db_employee)
        self.db.commit()
        return {'message': "Employee deleted successfully"}

    # For Department
    def setInDepart(self, department: Department) -> dict:
        # Check if department with same departId already exists
        existing = self.db.query(DepartmentModel).filter(DepartmentModel.departId == department.departId).first()
        if existing:
            return {'error': 'Department with this ID already exists'}

        db_department = DepartmentModel(
            departId=department.departId,
            departName=department.departName
        )
        self.db.add(db_department)
        self.db.commit()
        self.db.refresh(db_department)
        return {'message': "Department added successfully", 'id': db_department.id}

    def getDepartmentIndividual(self, departId: str) -> Optional[DepartmentModel]:
        return self.db.query(DepartmentModel).filter(DepartmentModel.departId == departId).first()

    def getDepartment(self) -> List[DepartmentModel]:
        return self.db.query(DepartmentModel).all()

    def updateInDepartment(self, departId: str, department_update: DepartmentUpdate) -> dict:
        db_department = self.db.query(DepartmentModel).filter(DepartmentModel.departId == departId).first()
        if not db_department:
            return {'error': 'Department not found'}

        update_data = department_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_department, field, value)

        self.db.commit()
        return {'message': "Department updated successfully"}

    def deleteInDepartment(self, departId: str) -> dict:
        db_department = self.db.query(DepartmentModel).filter(DepartmentModel.departId == departId).first()
        if not db_department:
            return {'error': 'Department not found'}

        self.db.delete(db_department)
        self.db.commit()
        return {'message': "Department deleted successfully"}