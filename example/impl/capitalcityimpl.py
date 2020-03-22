from dataclasses import dataclass

from dataclass_abc import resolve_abc_prop
from example.capitalcity import CapitalCity


@resolve_abc_prop
@dataclass
class CapitalCityImpl(CapitalCity):
    city_name: str
    lon: float
    lat: float
    country_name: str
