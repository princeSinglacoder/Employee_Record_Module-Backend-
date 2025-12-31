from app.database.database import Repository
from app.schemas.employee import Employee,EmployeeUpdate
from fastapi import HTTPException

class Employee_Service:
    def create(self,empId:str,employee: Employee):
        if empId in Repository.getEmployee():
            raise HTTPException(status_code=400, detail='Employee already exist')
        
        if employee.departId not in Repository.getDepartment():
            raise HTTPException(status_code=404, detail='Department not exist')
        
        return Repository.setInEmployee(empId,employee)

    def get(self,empId:str):
        if empId not in Repository.getEmployee():
            raise HTTPException(status_code=404, detail='Employee doesnt exist')
        
        return Repository.getEmployeeIndividual(empId)
    
    def update(self,empId:str,employeeUpdate: EmployeeUpdate):
        # first fetch actual data
        if empId not in Repository.getEmployee():
            raise HTTPException(status_code=404, detail='EmpId not found')
        
        existEmp = Repository.getEmployeeIndividual(empId)

        update_data =  employeeUpdate.model_dump(exclude_none=True)

        for key,value in update_data.items():
            setattr(existEmp,key,value)

        return Repository.updateInEmployee(empId,existEmp)

    def delete(self,empId:str):
        if empId not in Repository.getEmployee():
            raise HTTPException(status_code=404, detail='Employee Not Found')
        
        return  Repository.deleteInEmployee(empId)