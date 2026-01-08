from fastapi import HTTPException
from app.schemas.department import Department,DepartmentUpdate
from app.database.employeeDB import Repository

class Department_Service:
    def create(self,departId:str,department:Department):
        if departId in Repository.getDepartment():
            raise HTTPException(status_code=400, detail='Department already exist')

        return Repository.setInDepart(departId,department)
    
    def get(self,departId:str):
        if departId not in Repository.getDepartment():
            raise HTTPException(status_code=404, detail='Department doesnt exist')
        
        return Repository.getDepartmentIndividual(departId)
    
    def update(self,departId:str,departmentUpdate: DepartmentUpdate):
        # first fetch actual data
        if departId not in Repository.getDepartment():
            raise HTTPException(status_code=404, detail='departId not found')
        
        existDepart = Repository.getDepartmentIndividual(departId)

        update_data =  departmentUpdate.model_dump(exclude_none=True)

        for key,value in update_data.items():
            setattr(existDepart,key,value)

        return Repository.updateInDepartment(departId,existDepart)
    

    def delete(self,departId:str):
        if departId not in Repository.getDepartment():
            raise HTTPException(status_code=404, detail='Department Not Found')
    
        
        return  Repository.deleteInDepartment(departId)