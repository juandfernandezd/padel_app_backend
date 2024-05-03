from pydantic import BaseModel
from typing import Dict, List, Union

class Partido(BaseModel):
    pareja1Jugador1: str
    pareja1Jugador2: str
    pareja2Jugador1: str
    pareja2Jugador2: str
    numSets: int


class Puntaje(BaseModel):
    points_pareja_1: int = 0
    points_pareja_2: int = 0
    set_actual: int = 1
    sets_pareja_1: int = 0
    sets_pareja_2: int = 0
    history: List[Dict[str, int]] = []

class Saque(BaseModel):
    pareja: int

class WSMessage(BaseModel):
    msg_type: str
    content: Union[Dict, Partido, None]