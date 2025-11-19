# manager.py (versión simple)
from typing import List, Dict, Optional
from fastapi import WebSocket
from models import WSMessage

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.device_of: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.device_of[websocket] = "unknown"
        print(f'ws disconnected. active connections: {len(self.active_connections)}')

    def set_device(self, websocket: WebSocket, device: str):
        if websocket in self.device_of:
            self.device_of[websocket] = device

    def get_device(self, websocket: WebSocket) -> str:
        return self.device_of.get(websocket, "unknown")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.device_of.pop(websocket, None)
        print(f'ws disconnected. active connections: {len(self.active_connections)}')

    async def send_personal_message(self, message: WSMessage, websocket: WebSocket):
        try:
            await websocket.send_json(message.model_dump())
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: WSMessage, only_device: Optional[str] = None):
        payload = message.model_dump()
        for ws in list(self.active_connections):
            if only_device and self.device_of.get(ws) != only_device:
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(ws)
