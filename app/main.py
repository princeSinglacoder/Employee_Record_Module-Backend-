from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import init_database

from app.routes.employee_router import router as employee_router
from app.routes.department_router import router as department_router
from app.routes.auth import router as auth_router
from app.routes.leave_router import router as leave_router

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_database()

@app.get("/test")
def test():
    return {"message": "Backend is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router)
app.include_router(department_router)
app.include_router(auth_router)
app.include_router(leave_router)
