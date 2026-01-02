# Employee Module Backend

Backend system to manage employees and departments where Admin can register employees, manage departments, and provide login credentials.

## Features

### Employee Management
- Admin can **register employees**.
- Auto-generated **username and password** for employees.
- Employee data stored in-memory.
- Employees can **log in** using credentials.

### Department Management
- Admin can perform **CRUD operations** on departments:
  - **Create:** Add a new department.
  - **Read:** View department details.
  - **Update:** Edit department information.
  - **Delete:** Remove a department.

## Tech Stack
- Python
- FastAPI
- In-memory storage (dictionary)
- JWT authentication (if implemented)
