from fastapi import FastAPI, Request
from app.routes.employee_router import router as employee_router
from app.routes.department_router import router as department_router
from app.routes.auth import router as auth_router
from app.routes.leave_router import router as leave_router
from app.database.database import init_database
from fastapi.middleware.cors import CORSMiddleware

# Initialize database on startup
init_database()

app = FastAPI()

# Add a test endpoint to check if backend is reachable
@app.get("/test")
def test_connection(request: Request):
    return {
        "message": "Backend is running!",
        "origin": request.headers.get("origin", "No origin header"),
        "status": "ok"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:5500", 
        "http://127.0.0.1:5500", 
        "http://localhost:8080", 
        "http://127.0.0.1:8080", 
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "http://localhost:4200",  # Angular default
        "http://127.0.0.1:4200",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:63342",  # PyCharm/WebStorm
        "http://127.0.0.1:63342",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
    
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(auth_router)
app.include_router(leave_router)