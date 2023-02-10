from typing import TypedDict


class Ais(TypedDict):
    courseOverGround: float
    latitude: float
    longitude: float
    name: str
    rateOfTurn: int
    shipType: int
    speedOverGround: float
    trueHeading: int
    mmsi: int
    msgtime: str
    jurisdiction: str
    shipTypeTxt: str
