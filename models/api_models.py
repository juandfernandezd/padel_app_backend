from pydantic import BaseModel
from typing import Dict, Any, Union

class Partido(BaseModel):
    pareja1Jugador1: str
    pareja1Jugador2: str
    pareja2Jugador1: str
    pareja2Jugador2: str
    numSets: int

class WSMessage(BaseModel):
    msg_type: str
    content: Union[Dict, Partido, None]