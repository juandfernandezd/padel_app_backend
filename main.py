import uvicorn
import math
import time
import asyncio
import os
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    WebSocket, 
    WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware

from models import (
    ConnectionManager, 
    Partido,
    WSMessage
)

load_dotenv()
device = os.getenv('DEVICE', 'PC')

if device == 'PC':
    print('importing fake pigpio')
    from utils import fake_pigpio as pigpio
else:
    import pigpio
    
pi = pigpio.pi()

BOUNCE_TIME = 0.3

PAREJA1_PIN1 = 17
PAREJA1_PIN2 = 15
PAREJA2_PIN1 = 27
PAREJA2_PIN2 = 18

pines = [
    PAREJA1_PIN1,
    PAREJA1_PIN2,
    PAREJA2_PIN1,
    PAREJA2_PIN2
]

last_pressed = 0

for pin in pines:
    pi.set_mode(pin, pigpio.INPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_UP)


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
puntaje = None

# utils
def cambiar_set():
    puntaje['points_pareja_1'] = 0
    puntaje['points_pareja_2'] = 0
    puntaje['set_actual'] += 1

def cambiar_game():
    puntaje['points_pareja_1'] = 0
    puntaje['points_pareja_2'] = 0


async def cambiar_puntaje(p1: int, p2: int):
    set_changed = False
    score_sent = False
    pos_set = puntaje['set_actual'] - 1
    games_1 = puntaje['history'][pos_set][f'games_pareja_{p1}']
    games_2 = puntaje['history'][pos_set][f'games_pareja_{p2}']
    points_1 = puntaje[f'points_pareja_{p1}']
    points_2 = puntaje[f'points_pareja_{p2}']


    if games_1 == 6 and games_2 == 6:
        puntaje[f'points_pareja_{p1}'] += 1
        points_1 += 1

        if points_1 >= 7 and (points_1 - points_2 >= 2):
            puntaje['history'][pos_set][f'games_pareja_{p1}'] += 1
            games_1 += 1
            puntaje[f'sets_pareja_{p1}'] += 1
            cambiar_set()
            await send_score()
            set_changed = True
            score_sent = True
    else:
        if match.modoTorneo:
            if puntaje['sets_pareja_1'] == 1 and puntaje['sets_pareja_2'] == 1:
                puntaje[f'points_pareja_{p1}'] += 1
                points_1 += 1

                if points_1 >= 10 and (points_1 - points_2 >= 2):
                    puntaje['history'][pos_set][f'games_pareja_{p1}'] = points_1
                    puntaje['history'][pos_set][f'games_pareja_{p2}'] = points_2
                    puntaje[f'sets_pareja_{p1}'] += 1
            
            else:
                if points_1 in [0, 15]:
                    puntaje[f'points_pareja_{p1}'] += 15
                elif points_1 == 30:
                    puntaje[f'points_pareja_{p1}'] += 10
                elif points_1 == 40:
                    cambiar_game()
                    puntaje['history'][pos_set][f'games_pareja_{p1}'] += 1
                    games_1 += 1


        else:
            if points_1 in [0, 15]:
                puntaje[f'points_pareja_{p1}'] += 15
            elif points_1 == 30:
                puntaje[f'points_pareja_{p1}'] += 10
            elif points_1 == 40:
                cambiar_game()
                puntaje['history'][pos_set][f'games_pareja_{p1}'] += 1
                games_1 += 1

    if (games_1 == 6 and games_2 <= 4) or (games_1 == 7 and games_2 in [5, 6]) and not set_changed:
        cambiar_set()
        puntaje[f'sets_pareja_{p1}'] += 1

    if puntaje[f'sets_pareja_{p1}'] >= math.ceil(match.numSets / 2):
        await send_score()
        await enviar_finalizacion()

    if not score_sent:
        await send_score()

    return {
        'status': 'ok',
        'message': 'mensaje enviado con exito a todos los peers'
    }


async def enviar_finalizacion():
    global match, puntaje

    await manager.broadcast(
        WSMessage(msg_type='info', content={'msg': construir_mensaje()})
    )

    await asyncio.sleep(10)

    match = None
    puntaje = None

    await manager.broadcast(
        WSMessage(msg_type='match', content=match)
    )


def construir_mensaje():
    msg = ''
    if puntaje['sets_pareja_1'] > puntaje['sets_pareja_2']:
        msg = f'Felicitaciones {match.pareja1Jugador1} y {match.pareja1Jugador2} han ganado el partido..!'
    
    elif puntaje['sets_pareja_2'] > puntaje['sets_pareja_1']:
        msg = f'Felicitaciones {match.pareja2Jugador1} y {match.pareja2Jugador2} han ganado el partido..!'
    
    else:
        msg = 'El partido ha quedado en empate'

    return msg


# websocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.broadcast(
        WSMessage(msg_type='match', content=match)
    )
    await send_score()

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
        WSMessage(msg_type='score', content=puntaje)
    )

# endpoints

@app.post("/registro_partido")
async def registro_partido(partido: Partido):
    global match, puntaje
    match = partido

    history = [{'games_pareja_1': 0, 'games_pareja_2': 0} for _ in range(partido.numSets)]

    puntaje = {
        'points_pareja_1': 0,
        'points_pareja_2': 0,
        'set_actual': 1,
        'sets_pareja_1': 0,
        'sets_pareja_2': 0,
        'history': history
    }

    await manager.broadcast(
        WSMessage(msg_type='match', content=match)
    )

    await manager.broadcast(
        WSMessage(msg_type='score', content=puntaje)
    )

@app.get("/obtener_partido")
async def obtener_partido():
    return {
        'match': match,
        'status': 'ok'
    }


@app.get('/enviar_puntaje/{pin}')
async def enviar_puntaje(pin: int):

    if pin in [PAREJA1_PIN1, PAREJA1_PIN2]:
        await cambiar_puntaje(p1=1, p2=2)
    else:
        await cambiar_puntaje(p1=2, p2=1)

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
    global match

    if match:
        await enviar_finalizacion()

    return {
        'status': 'ok',
        'message': 'se ha finalizado el partido'
    }

# buttons handle

def handle_button_pareja_1(gpio, level, tick):
    global last_pressed, match

    if not match:
        return

    current_time = time.time()

    # Ignora si el evento ocurre dentro del tiempo de rebote
    if gpio in [PAREJA1_PIN1, PAREJA1_PIN2]:
        if (current_time - last_pressed) < BOUNCE_TIME:
            return
        last_pressed = current_time

    if level == 0:  # Nivel bajo indica que el botón está presionado
        asyncio.run(cambiar_puntaje(p1=1, p2=2))


def handle_button_pareja_2(gpio, level, tick):
    global last_pressed, match

    if not match:
        return

    current_time = time.time()

    if gpio in [PAREJA2_PIN1, PAREJA2_PIN2]:
        if (current_time - last_pressed) < BOUNCE_TIME:
            return
        last_pressed = current_time

    if level == 0:
        asyncio.run(cambiar_puntaje(p1=2, p2=1))


pi.callback(PAREJA1_PIN1, pigpio.EITHER_EDGE, handle_button_pareja_1)
pi.callback(PAREJA1_PIN2, pigpio.EITHER_EDGE, handle_button_pareja_1)
pi.callback(PAREJA2_PIN1, pigpio.EITHER_EDGE, handle_button_pareja_2)
pi.callback(PAREJA2_PIN2, pigpio.EITHER_EDGE, handle_button_pareja_2)

# server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
