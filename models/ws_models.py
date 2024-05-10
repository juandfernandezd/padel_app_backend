from fastapi import WebSocket
from models import WSMessage

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f'active connections: {len(self.active_connections)}')

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: WSMessage, websocket: WebSocket):
        print(message)
        await websocket.send_json(message.model_dump())

    async def broadcast(self, message: WSMessage):
        try:
            for connection in self.active_connections:
                await connection.send_json(message.model_dump())
        except:
            self.active_connections.remove(connection)
            print('ws connection not found')