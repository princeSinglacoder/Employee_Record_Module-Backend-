from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import init_database

from app.routes.employee_router import router as employee_router
from app.routes.department_router import router as department_router
from app.routes.auth_router import router as auth_router
from app.routes.leave_router import router as leave_router
from app.routes.notification_router import router as notification_router

app = FastAPI()

# -------------------- STARTUP EVENT --------------------
@app.on_event("startup")
def startup_event():
    init_database()

# -------------------- TEST ENDPOINT --------------------
@app.get("/test")
def test():
    return {"message": "Backend is running"}

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*", # Allow all origins (compatible with credentials)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- ROUTERS --------------------
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(auth_router)
app.include_router(leave_router)
app.include_router(notification_router)
