from fastapi import APIRouter, HTTPException,Depends,status   
from app.schemas.employee import Employee,TempEmployee
from app.services.employee_service import Employee_Service
from app.database.database import Repository
from app.schemas.user import UserLogIn,EmployeeUserLogIn
from app.database.user_repo import UserRepository
from app.utils.jwt import get_current_user
import uuid

router = APIRouter(prefix="/employee")

empService = Employee_Service()


@router.get("/")   # get all data
def get_all_employees(current_user = Depends(get_current_user)):

    # no need to check the role
    return Repository.getEmployee()

@router.get("/{userName}")  # get particular data
def get_employee(userName:str,current_user=Depends(get_current_user)):
    return empService.get(userName)


@router.post('/register')
def register_employee(tempEmployee:TempEmployee,current_user = Depends(get_current_user)):
    # role check
    if current_user['role']!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only admin can register employee")
    
    # Generate Credentials
    username = f"EMP-{uuid.uuid4().hex[:6]}"
    password = "123456"

    # Create employee object
    employee = Employee(**tempEmployee.dict(),userName=username,password=password)


    # Now save that employee in first DB
    empService.create(username,employee)
    # Repository.setInEmployee(employee.userName,employee)


    # We save in Second DB where we set every user as an employee
    UserRepository.add_user(
        EmployeeUserLogIn(userName=employee.userName,password=employee.password)
    )

    # return username and password as response
    return {
        "message": "Employee registered successfully",
        "username": employee.userName,
        "password": employee.password
    }


@router.put("/{userName}") 
def update_employee(userName:str,employeeUpdate: Employee,current_user = Depends(get_current_user)):
    if current_user['role']!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admin allowed')
    
    return empService.update(userName,employeeUpdate)

@router.delete("/{userName}")
def delete_employee(userName:str,current_user = Depends(get_current_user)):
    if current_user['role']!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admin allowed')
    
    return empService.delete(userName)