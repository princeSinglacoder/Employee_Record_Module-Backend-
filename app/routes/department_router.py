from fastapi import APIRouter,HTTPException, Request
from app.schemas.department import Department,DepartmentUpdate
from app.services.department_service import Department_Service
from app.database.employeeDB import Repository
from app.utils.jwt import get_current_user

router = APIRouter(prefix='/department')

departService = Department_Service()

@router.post("/")
def create_department(department: Department, request: Request):
    current_user = get_current_user(request)
    if current_user['role']!= 'admin':
        raise HTTPException(status_code=403, detail='Only admin can create department')

    departService.create(department.departId,department)
    return {"message":"Department created successfully"}

@router.get("/{departId}")
def get_department(departId:str , request: Request):
    current_user = get_current_user(request)
    return departService.get(departId)

@router.get("/")
def get_all_departments(request: Request):
    current_user = get_current_user(request)
    return Repository.getDepartment()


@router.put("/{departId}")
def update_department(departId:str,departmentUpdate: DepartmentUpdate, request: Request):
    current_user = get_current_user(request)
    if current_user['role']!='admin':
        raise HTTPException(status_code=403, detail='Only admin can update department')
    
    return departService.update(departId,departmentUpdate)

@router.delete("/{departId}")
def delete_department(departId:str, request: Request):
    current_user = get_current_user(request)
    if current_user['role']!='admin':
        raise HTTPException(status_code=403, detail='Only admin can delete department')
    
    return departService.delete(departId)
