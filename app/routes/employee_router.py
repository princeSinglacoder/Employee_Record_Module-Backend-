from fastapi import APIRouter, HTTPException, status, Request, Depends
from app.schemas.employee import Employee, TempEmployee, UpdateEmployee
from app.services.employee_service import Employee_Service
from app.database.employeeDB import Repository
from app.schemas.user import EmployeeUserLogIn
from app.database.user_repo import UserRepository
from app.utils.jwt import get_current_user
from app.config import get_db
from sqlalchemy.orm import Session
import uuid
from app.websocket.notification_ws import manager

router = APIRouter(prefix="/employee")

@router.get("/")   # get all data
def get_all_employees(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admin can access all employees')

    repo = Repository(db)
    return repo.getEmployee()

@router.get("/{userName}")  # get particular data
def get_employee(userName: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user['role'] == 'admin' or current_user['userName'] == userName:
        emp_service = Employee_Service(db)
        return emp_service.get(userName)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You can access only your data')

@router.post('/register')
async def register_employee(
    tempEmployee: TempEmployee,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request)

    # role check
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can register employee"
        )

    # Generate Credentials
    username = f"EMP-{uuid.uuid4().hex[:6]}"
    password = "123456"

    emp_service = Employee_Service(db)
    if emp_service.checkExist(username):
        raise HTTPException(
            status_code=400,
            detail="Username already exists, try again"
        )

    # Create employee object
    employee = Employee(
        **tempEmployee.model_dump(),
        userName=username,
        password=password
    )

    # Now save that employee in first DB
    result = emp_service.create(employee)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])

    # We save in Second DB where we set every user as an employee
    user_repo = UserRepository(db)
    user_repo.add_user(
        EmployeeUserLogIn(
            userName=employee.userName,
            password=employee.password,
            role='employee'
        )
    )

    # 🔔 Notify only that employee (WELCOME)
    from app.websocket.notification_ws import manager
    await manager.notify_employee(
        employee.id,
        {
            "type": "WELCOME",
            "message": "Welcome to our company 🎉"
        }
    )

    # return username and password as response
    return {
        "message": "Employee registered successfully",
        "username": employee.userName,
        "password": employee.password
    }


@router.put("/{userName}")
async def update_employee(
    userName: str,
    employeeUpdate: UpdateEmployee,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request)
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only admin allowed'
        )

    emp_service = Employee_Service(db)

    # Update employee
    result = emp_service.update(userName, employeeUpdate)

    # Get employee after update
    employee = emp_service.get(userName)

    # 🔔 Notify only that employee
    try:
        from app.websocket.notification_ws import manager
        await manager.notify_employee(
            employee.id,
            {
                "type": "EMPLOYEE_UPDATED",
                "message": "Your profile details have been updated"
            }
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

    return result


@router.delete("/{userName}")
def delete_employee(userName: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admin allowed')

    emp_service = Employee_Service(db)
    return emp_service.delete(userName)