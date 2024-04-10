import uvicorn
import math
from fastapi import (
    FastAPI,
    WebSocket, 
    WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware
from models import (
    ConnectionManager, 
    Partido,
    PuntajeActual,
    Puntaje,
    WSMessage
)


app = FastAPI()
origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init config
manager = ConnectionManager()
match = None
puntaje_actual = None
puntaje_pareja_1 = None
puntaje_pareja_2 = None
# referencia a los pines GPIO
pin_pareja1 = 17
pin_pareja2 = 18


# utils
def cambiar_set():
    puntaje_pareja_1.points = 0
    puntaje_pareja_2.points = 0
    puntaje_pareja_1.games = 0
    puntaje_pareja_2.games = 0
    puntaje_actual.set += 1

def cambiar_game():
    puntaje_pareja_1.points = 0
    puntaje_pareja_2.points = 0

async def cambiar_puntaje(puntaje1: Puntaje, puntaje2: Puntaje):
    global puntaje_actual, match
    if puntaje1.games == 6 and puntaje2.games == 6:
        puntaje1.points += 1

        if puntaje1.points >= 7 and (puntaje1.points - puntaje2.points) >= 2:
            puntaje1.games += 1
            puntaje1.sets += 1
            await send_score()
            cambiar_set()
    else:
        if puntaje1.points in [0, 15]:
            puntaje1.points += 15
        elif puntaje1.points == 30:
            puntaje1.points += 10
        elif puntaje1.points == 40:
            cambiar_game()
            puntaje1.games += 1

    if (puntaje1.games == 6 and puntaje2.games <= 4) or (puntaje1.games == 7 and puntaje2.games in [5, 6]):
        await send_score()
        cambiar_set()
        puntaje1.sets += 1


    if puntaje1.sets >= math.ceil(match.numSets / 2):
        await send_score()
        await enviar_finalizacion()

    await send_score()

    return {
        'status': 'ok',
        'message': 'mensaje enviado con exito a todos los peers'
    }

async def enviar_finalizacion():
    global match, puntaje_actual, puntaje_pareja_1, puntaje_pareja_2

    await manager.broadcast(
        WSMessage(msg_type='info', content={'msg': construir_mensaje()})
    )

    match = None
    puntaje_actual = None
    puntaje_pareja_1 = None
    puntaje_pareja_2 = None

    await manager.broadcast(
        WSMessage(msg_type='match', content=match)
    )


def construir_mensaje():
    msg = ''
    if puntaje_pareja_1.sets > puntaje_pareja_2.sets:
        msg = f'Felicitaciones {match.pareja1Jugador1} y {match.pareja1Jugador2} han ganado el partido..!'
    
    elif puntaje_pareja_2.sets > puntaje_pareja_1.sets:
        msg = f'Felicitaciones {match.pareja2Jugador1} y {match.pareja2Jugador2} han ganado el partido..!'
    
    else:
        msg = 'El partido ha quedado en empate'

    return msg


# websocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            await manager.send_personal_message(
                WSMessage(msg_type='echo', content={'msg': msg}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def send_score():
    await manager.broadcast(
        WSMessage(msg_type='score', content=puntaje_actual)
    )


# endpoints

@app.post("/registro_partido")
async def registro_partido(partido: Partido):
    global match, puntaje_actual, puntaje_pareja_1, puntaje_pareja_2
    match = partido
    puntaje_pareja_1 = Puntaje()
    puntaje_pareja_2 = Puntaje()
    puntaje_actual = PuntajeActual(
        puntaje_pareja_1=puntaje_pareja_1,
        puntaje_pareja_2=puntaje_pareja_2,
        set=1
    )
    await manager.broadcast(
        WSMessage(msg_type='match', content=match)
    )

@app.get("/obtener_partido")
async def obtener_partido():
    return {
        'match': match,
        'status': 'ok'
    }


@app.get('/enviar_puntaje/{pin}')
async def enviar_puntaje(pin: int):

    if pin == pin_pareja1:
        await cambiar_puntaje(puntaje_pareja_1, puntaje_pareja_2)
    else:
        await cambiar_puntaje(puntaje_pareja_2, puntaje_pareja_1)

    return {
        'status': 'ok',
        'message': 'mensaje enviado con exito a todos los peers'
    }


@app.post('/cambiar_saque/{pareja}')
async def cambiar_saque(pareja: int):
    await manager.broadcast(
        WSMessage(msg_type='serve', content={'pareja': pareja})
    )
    return {
        'status': 'ok',
        'message': 'mensaje enviado con exito a todos los peers'
    }


@app.get('/finalizar_partido')
async def finalizar_partido():
    await enviar_finalizacion()
    return {
        'status': 'ok',
        'message': 'se ha finalizado el partido'
    }

# server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)