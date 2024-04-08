import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models import (ConnectionManager, Partido, Puntaje, Saque, WSMessage)


app = FastAPI()
origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

match = None
manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Espera mensajes del cliente, pero en este caso no se hace nada con ellos
            msg = await websocket.receive_text()
            await manager.send_personal_message(
                WSMessage(msg_type='echo', content={'msg': msg}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/registro_partido")
async def registro_partido(partido: Partido):
    global match
    print(f'receiving new match... {partido}')
    match = partido
    await manager.broadcast(
        WSMessage(msg_type='match', content=match)
    )

@app.get("/obtener_partido")
async def obtener_partido():
    return {
        'match': match,
        'status': 'ok'
    }

@app.post('/enviar_puntaje')
async def enviar_puntaje(puntaje: Puntaje):
    await manager.broadcast(
        WSMessage(msg_type='score', content={'pareja': puntaje.pareja, 'games': puntaje.games})
    )
    return {
        'status': 'ok',
        'message': 'mensaje enviado con exito a todos los peers'
    }

@app.post('/cambiar_saque')
async def cambiar_saque(saque: Saque):
    await manager.broadcast(
        WSMessage(msg_type='serve', content={'pareja': saque.pareja, 'jugador': saque.jugador})
    )
    return {
        'status': 'ok',
        'message': 'mensaje enviado con exito a todos los peers'
    }


@app.get('/finalizar_partido')
async def finalizar_partido():
    global match
    match = None
    await manager.broadcast(WSMessage(msg_type='match', content=match))
    return {
        'status': 'ok',
        'message': 'se ha finalizado el partido'
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)