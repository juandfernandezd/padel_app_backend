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

PIN1_PAREJA1 = 17
PIN2_PAREJA1 = 15

PIN1_PAREJA2 = 27
PIN2_PAREJA2 = 18

last_pressed_pin_11 = 0
last_pressed_pin_22 = 0

pi.set_mode(PIN1_PAREJA1, pigpio.INPUT)
pi.set_pull_up_down(PIN1_PAREJA1, pigpio.PUD_UP)

pi.set_mode(PIN2_PAREJA2, pigpio.INPUT)
pi.set_pull_up_down(PIN2_PAREJA2, pigpio.PUD_UP)


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
            await send_score()
            cambiar_set()
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

    if (games_1 == 6 and games_2 <= 4) or (games_1 == 7 and games_2 in [5, 6]):
        cambiar_set()
        puntaje[f'sets_pareja_{p1}'] += 1

    if puntaje[f'sets_pareja_{p1}'] >= math.ceil(match.numSets / 2):
        await send_score()
        await enviar_finalizacion()

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

    if pin in [PIN1_PAREJA1, PIN2_PAREJA1]:
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

def handle_button_pareja1(gpio, level, tick):
    global last_pressed_pin_11, match

    current_time = time.time()

    # Ignora si el evento ocurre dentro del tiempo de rebote
    if gpio == PIN1_PAREJA1:
        if (current_time - last_pressed_pin_11) < BOUNCE_TIME:
            return
        last_pressed_pin_11 = current_time

    if level == 0 and match:  # Nivel bajo indica que el botón está presionado
        print(f"Button on pin {gpio} was pressed!")
        asyncio.run(cambiar_puntaje(p1=1, p2=2))


def handle_button_pareja2(gpio, level, tick):
    global last_pressed_pin_22, match

    current_time = time.time()

    # Ignora si el evento ocurre dentro del tiempo de rebote
    if gpio == PIN2_PAREJA2:
        if (current_time - last_pressed_pin_22) < BOUNCE_TIME:
            return
        last_pressed_pin_22 = current_time

    if level == 0 and match:  # Nivel bajo indica que el botón está presionado
        print(f"Button on pin {gpio} was pressed!")
        asyncio.run(cambiar_puntaje(p1=2, p2=1))


pi.callback(PIN1_PAREJA1, pigpio.EITHER_EDGE, handle_button_pareja1)
pi.callback(PIN2_PAREJA2, pigpio.EITHER_EDGE, handle_button_pareja2)

# server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
