from dataclasses import dataclass

from dataclass_abc import resolve_abc_prop
from example.city import City


@resolve_abc_prop
@dataclass
class CityImpl(City):
    city_name: str
    lon: float
    lat: float
