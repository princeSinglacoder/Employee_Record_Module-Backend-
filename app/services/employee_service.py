from app.database.employeeDB import Repository
from app.schemas.employee import Employee,TempEmployee,UpdateEmployee
from fastapi import HTTPException

class Employee_Service:
    def create(self,userName:str,employee: Employee):
        
        if employee.departId not in Repository.getDepartment():
            raise HTTPException(status_code=404, detail='Department not exist')
        
        return Repository.setInEmployee(userName,employee)

    def get(self,userName:str):
        if userName not in Repository.getEmployee():
            raise HTTPException(status_code=404, detail='Employee doesnt exist')
        
        return Repository.getEmployeeIndividual(userName)
    
    def update(self,userName:str,employeeUpdate: UpdateEmployee):
        # first fetch actual data
        if userName not in Repository.getEmployee():
            raise HTTPException(status_code=404, detail='UserName not found')
        
        existEmp = Repository.getEmployeeIndividual(userName)

        update_data =  employeeUpdate.model_dump(exclude_none=True)

        for key,value in update_data.items():
            setattr(existEmp,key,value)

        return Repository.updateInEmployee(userName,existEmp)

    def delete(self,userName:str):
        if userName not in Repository.getEmployee():
            raise HTTPException(status_code=404, detail='Employee Not Found')
        
        return  Repository.deleteInEmployee(userName)