from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.notification_ws import manager

router = APIRouter()

@router.websocket("/ws/notifications/{employee_id}")
async def notification_socket(websocket: WebSocket, employee_id: int):
    await manager.connect(employee_id, websocket)
    try:
        while True:
            # Keep connection alive, maybe handle incoming pings
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(employee_id)

@router.websocket("/ws_test")
async def websocket_test(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connected to test endpoint")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
