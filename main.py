import uvicorn
import json
import math
import asyncio
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


async def cambiar_puntaje(p1: int):
    p2 = 3 - p1
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
    try:

        if match:
            # enviar datos del partido y del puntaje solo al dispositivo que se acaba de conectar
            await manager.send_personal_message(
                WSMessage(msg_type="match", content=match),
                websocket
            )
            await manager.send_personal_message(
                WSMessage(msg_type="score", content=puntaje),
                websocket
            )

        while True:
            ws_msg = await websocket.receive_json()
            msg_type = ws_msg.get("msg_type")
            content  = ws_msg.get("content", {})

            match msg_type:
                case "hello":
                    device_type = ws_msg.get("device", "unknown")
                    manager.set_device(websocket, device_type)

                case "score":
                    if not match:
                        await manager.send_personal_message(
                            WSMessage(msg_type="echo", content={"message": "No hay un partido en curso", "status": "error"}),
                            websocket
                        )
                        continue

                    team = int(content.get("team"))
                    await cambiar_puntaje(p1=team)

                case _:
                    await manager.send_personal_message(
                        WSMessage(msg_type="echo", content=ws_msg),
                        websocket
                    )

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


async def send_score():
    await manager.broadcast(
        WSMessage(msg_type='score', content=puntaje), only_device="screen"
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
        WSMessage(msg_type='match', content=match),
        only_device="screen"
    )

    await manager.broadcast(
        WSMessage(msg_type='score', content=puntaje),
        only_device="screen"
    )

@app.get("/obtener_partido")
async def obtener_partido():
    return {
        'match': match,
        'status': 'ok'
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


# server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
