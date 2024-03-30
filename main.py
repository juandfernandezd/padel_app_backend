import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import sqlite3


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

match = {}

class Partido(BaseModel):
    pareja1Jugador1: str
    pareja1Jugador2: str
    pareja2Jugador1: str
    pareja2Jugador2: str
    numSets: int
    saqueRandom: bool
    puntoOro: bool
    estado: bool

def connect_db():
    # Conexión a la base de datos
    print("entra a connect_db")
    conn = sqlite3.connect('partidos.db')
    c = conn.cursor()

    # Creación de la tabla si no existe
    c.execute('''CREATE TABLE IF NOT EXISTS partidos
                 (id INTEGER PRIMARY KEY, 
                 pareja1Jugador1 TEXT, 
                 pareja1Jugador2 TEXT,
                 pareja2Jugador1 TEXT, 
                 pareja2Jugador2 TEXT, 
                 numSets INTEGER,
                 saqueRandom INTEGER,
                 puntoOro INTEGER,
                 estado INTEGER)''')
    conn.commit()
    conn.close()
    print("termino connect_db")

# Función para obtener el último partido activo
def obtener_ultimo_partido():
    conn = sqlite3.connect('partidos.db')
    c = conn.cursor()
    # Selecciona el último partido activo
    c.execute('''SELECT * FROM partidos WHERE estado = 1 ORDER BY id DESC LIMIT 1''')
    partido = c.fetchone()
    conn.close()
    return partido


@app.post("/registro_partido")
async def registro_partido(partido: Partido):
    connect_db()
    print(partido)
    print(f'receiving new match... {partido}')
    conn = sqlite3.connect('partidos.db')
    c = conn.cursor()
    partido_dict = jsonable_encoder(partido)
    c.execute('''INSERT INTO partidos 
                 (pareja1Jugador1, pareja1Jugador2, pareja2Jugador1, pareja2Jugador2, 
                 numSets, saqueRandom, puntoOro, estado) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (partido_dict['pareja1Jugador1'], partido_dict['pareja1Jugador2'],
                 partido_dict['pareja2Jugador1'], partido_dict['pareja2Jugador2'],
                 partido_dict['numSets'], partido_dict['saqueRandom'],
                 partido_dict['puntoOro'], 1 if partido_dict['estado'] else 0))
    conn.commit()
    conn.close()
    
    global match
    print(f'receiving new match... {partido}')
    match = partido
    return partido

@app.get("/obtener_partido")
async def obtener_partido():
    partido = obtener_ultimo_partido()
    if partido:
        # Si hay un partido activo, devuelve la información del partido
        return {
            "pareja1Jugador1": partido[1],
            "pareja1Jugador2": partido[2],
            "pareja2Jugador1": partido[3],
            "pareja2Jugador2": partido[4],
            "numSets": partido[5],
            "saqueRandom": partido[6],
            "puntoOro": partido[7],
            "estado": partido[8]
        }
    else:
        # Si no hay un partido activo, devuelve un JSON vacío
        return {}

    return match


if __name__ == "__main__":
    print("Iniciando la aplicación...")
    connect_db()
    print("Aplicación iniciada. Ejecutando el servidor FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8000)