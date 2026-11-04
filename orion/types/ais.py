from typing import Literal, Optional, TypedDict


class Ais(TypedDict, total=False):
    courseOverGround: float
    latitude: float
    longitude: float
    name: str
    rateOfTurn: int
    shipType: int
    speedOverGround: float
    trueHeading: int
    navigationalStatus: int
    mmsi: int
    msgtime: str
    stream: Optional[Literal["terra", "satellite", "offshore"]]
    jurisdiction: str
    shipTypeTxt: str
