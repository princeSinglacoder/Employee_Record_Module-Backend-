from fastapi import APIRouter, HTTPException
from app.schemas.employee import Employee,EmployeeUpdate
from app.services.employee_service import Employee_Service
from app.database.database import Repository
from app.schemas.user import UserCreate,TempUserCreate
from app.database.user_repo import UserRepository

router = APIRouter(prefix="/employee")

empService = Employee_Service()


@router.post('/register')
def register(tempUserCreate:TempUserCreate):
    user = UserCreate(**tempUserCreate.dict())

    if not UserRepository.add_user(user):
        raise HTTPException(status_code=400,detail='User already exists')
    
    return {'message':'User add SuccessFully'}

@router.get("/")   # get all data
def get_all_employees():
    return Repository.getEmployee()

@router.get("/{emp_id}")  # get particular data
def get_employee(emp_id:str):
    return empService.get(emp_id)

@router.post("/")  # when admin hit a 'add' button then this router must be call
def create_employee(employee: Employee):
    return empService.create(employee.empId,employee)

@router.put("/{emp_id}") 
def update_employee(emp_id:str,employeeUpdate: EmployeeUpdate):
    return empService.update(emp_id,employeeUpdate)

@router.delete("/{emp_id}")
def delete_employee(emp_id:str):
    return empService.delete(emp_id)