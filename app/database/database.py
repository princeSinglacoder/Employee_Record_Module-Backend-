from app.schemas.employee import Employee,EmployeeUpdate
from app.schemas.department import Department,DepartmentUpdate

class Repository:
    __employee = {}
    __department = {}


    # For Employee
    @classmethod
    def setInEmployee(cls,key:str,value:Employee):
        cls.__employee[key]=value
        return  {'message': "Employee Add successfully"}

    @classmethod
    def getEmployeeIndividual(cls,key:str):
        return cls.__employee[key]
    
    @classmethod
    def getEmployee(cls):
        return cls.__employee

    @classmethod
    def updateInEmployee(cls,key:str,value:Employee):
        cls.__employee[key]=value
        return {'message': "Employee update SuccessFully"}


    @classmethod
    def deleteInEmployee(cls,key:str):
        del cls.__employee[key]
        return {'message': "Employee delete Successfully"}
    

    # For department
    @classmethod
    def setInDepart(cls,key:str,value:Department):
        cls.__department[key]=value
        return {'message': "Department Add successfully"}
    
    @classmethod
    def getDepartmentIndividual(cls,key:str):
        return cls.__department[key]
    
    @classmethod
    def getDepartment(cls):
        return cls.__department
    
    @classmethod
    def updateInDepartment(cls,key:str,value:Department):
        cls.__department[key]=value
        return {'message': "Department update SuccessFully"}
    
    @classmethod
    def deleteInDepartment(cls,key:str):
        del cls.__department[key]
        return {'message': "Department delete Successfully"}