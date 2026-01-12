from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.department import Department, DepartmentUpdate
from app.services.department_service import Department_Service
from app.database.employeeDB import Repository
from app.utils.jwt import get_current_user
from sqlalchemy.orm import Session
from app.config import get_db

router = APIRouter(prefix='/department')

@router.post("/")
def create_department(department: Department, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can create department')

    depart_service = Department_Service(db)
    result = depart_service.create(department)
    return result

@router.get("/{departId}")
def get_department(departId: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    depart_service = Department_Service(db)
    return depart_service.get(departId)

@router.get("/")
def get_all_departments(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    repo = Repository(db)
    return repo.getDepartment()

@router.put("/{departId}")
def update_department(departId: str, departmentUpdate: DepartmentUpdate, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can update department')

    depart_service = Department_Service(db)
    return depart_service.update(departId, departmentUpdate)

@router.delete("/{departId}")
def delete_department(departId: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can delete department')

    depart_service = Department_Service(db)
    return depart_service.delete(departId)
