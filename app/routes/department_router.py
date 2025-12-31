from fastapi import APIRouter,HTTPException
from app.schemas.department import Department,DepartmentUpdate
from app.services.department_service import Department_Service
from app.database.database import Repository

router = APIRouter(prefix='/department')

departService = Department_Service()

@router.post("/")
def create_department(department: Department):
    return departService.create(department.departId,department)

@router.get("/{departId}")
def get_department(departId:str):
    return departService.get(departId)

@router.get("/")
def get_all_departments():
    return Repository.getDepartment()


@router.put("/{departId}")
def update_department(departId:str,departmentUpdate: DepartmentUpdate):
    return departService.update(departId,departmentUpdate)

@router.delete("/{departId}")
def delete_department(departId:str):
    return departService.delete(departId)
