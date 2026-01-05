from fastapi import FastAPI
from app.routes.employee_router import router as employee_router
from app.routes.department_router import router as department_router
from app.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
    
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
