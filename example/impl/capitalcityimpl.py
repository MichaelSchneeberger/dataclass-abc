from dataclassabc import dataclassabc
from example.capitalcity import CapitalCity


@dataclassabc
class CapitalCityImpl(CapitalCity):
    city_name: str
    lon: float
    lat: float
    country_name: str
