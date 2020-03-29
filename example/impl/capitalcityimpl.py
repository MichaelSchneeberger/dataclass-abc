from dataclass_abc import dataclass_abc
from example.capitalcity import CapitalCity


@dataclass_abc
class CapitalCityImpl(CapitalCity):
    city_name: str
    lon: float
    lat: float
    country_name: str
