from dataclassabc import dataclassabc
from example.city import City


@dataclassabc
class CityImpl(City):
    city_name: str
    lon: float
    lat: float
