import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


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


@app.post("/registro_partido")
async def registro_partido(partido: Partido):
    global match
    print(f'receiving new match... {partido}')
    match = partido
    return partido

@app.get("/obtener_partido")
async def obtener_partido():
    return match


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)