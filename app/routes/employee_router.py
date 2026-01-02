from fastapi import APIRouter, HTTPException,Depends    
from app.schemas.employee import Employee,TempEmployee
from app.services.employee_service import Employee_Service
from app.database.database import Repository
from app.schemas.user import UserCreate,TempUserCreate
from app.database.user_repo import UserRepository
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/employee")

empService = Employee_Service()


@router.get("/")   # get all data
def get_all_employees():
    return Repository.getEmployee()

@router.get("/{emp_id}")  # get particular data
def get_employee(emp_id:str):
    return empService.get(emp_id)

# @router.post("/")  # when admin hit a 'add' button then this router must be call
# def create_employee(employee: Employee):
#     return empService.create(employee.empId,employee)

@router.post('/register')
def create_employee(employee: TempEmployee,current_user = Depends(get_current_user)):


@router.put("/{emp_id}") 
def update_employee(emp_id:str,employeeUpdate: EmployeeUpdate):
    return empService.update(emp_id,employeeUpdate)

@router.delete("/{emp_id}")
def delete_employee(emp_id:str):
    return empService.delete(emp_id)