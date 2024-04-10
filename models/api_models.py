from pydantic import BaseModel
from typing import Dict, Any, Union

class Partido(BaseModel):
    pareja1Jugador1: str
    pareja1Jugador2: str
    pareja2Jugador1: str
    pareja2Jugador2: str
    numSets: int


class Puntaje(BaseModel):
    points: int = 0
    games: int = 0
    sets: int = 0

class PuntajeActual(BaseModel):
    puntaje_pareja_1: Puntaje
    puntaje_pareja_2: Puntaje
    set: int

class Saque(BaseModel):
    pareja: int

class WSMessage(BaseModel):
    msg_type: str
    content: Union[Dict, Partido, PuntajeActual, None]