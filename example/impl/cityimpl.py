from dataclass_abc import dataclass_abc
from example.city import City


@dataclass_abc
class CityImpl(City):
    city_name: str
    lon: float
    lat: float
