from abc import ABC, abstractmethod
from math import radians, sin, cos, asin, sqrt
from dataclassabc import dataclassabc


class CityNameMixin(ABC):
    @property
    @abstractmethod
    def city_name(self) -> str: ...


class CountryNameMixin(ABC):
    @property
    @abstractmethod
    def country_name(self) -> str: ...


class SpherePositionMixin(ABC):
    @property
    @abstractmethod
    def lon(self) -> float: ...

    @property
    @abstractmethod
    def lat(self) -> float: ...

    def distance_to(
        self,
        other: "SpherePositionMixin",
    ) -> float:
        r = 6371  # Earth radius in kilometers
        lam_1, lam_2 = radians(self.lon), radians(other.lon)
        phi_1, phi_2 = radians(self.lat), radians(other.lat)
        h = (
            sin((phi_2 - phi_1) / 2) ** 2
            + cos(phi_1) * cos(phi_2) * sin((lam_2 - lam_1) / 2) ** 2
        )
        return 2 * r * asin(sqrt(h))


class City(CityNameMixin, SpherePositionMixin, ABC):
    pass


class CapitalCity(CountryNameMixin, City, ABC):
    pass


@dataclassabc
class CityImpl(City):
    city_name: str
    lon: float
    lat: float


def init_city(
    name: str,
    lon: float,
    lat: float,
):
    return CityImpl(
        city_name=name,
        lon=lon,
        lat=lat,
    )


@dataclassabc
class CapitalCityImpl(CapitalCity):
    city_name: str
    lon: float
    lat: float
    country_name: str


def init_capital_city(
    name: str,
    lon: float,
    lat: float,
    country: str,
):
    return CapitalCityImpl(city_name=name, lon=lon, lat=lat, country_name=country)


oslo = init_capital_city(
    name='Oslo',
    lon=10.8,
    lat=59.9,
    country='Norway',
)

madrid = init_capital_city(
    name='Madrid',
    lon=-3.7,
    lat=40.4,
    country='Spain',
)

zurich = init_city(
    name='Zurich',
    lon=8.6,
    lat=47.4,
)

cities = [oslo, madrid, zurich]

# filter capital cities
capitals = [city for city in cities if isinstance(city, CapitalCity)]

print(f'{madrid.distance_to(zurich)=}') # Output will be madrid.distance_to(zurich)=1253.2717264052803

# Output will be 
# capitals=[
#   CapitalCityImpl(city_name='Oslo', lon=10.8, lat=59.9, country_name='Norway'), 
#   CapitalCityImpl(city_name='Madrid', lon=-3.7, lat=40.4, country_name='Spain')]
print(f'{capitals=}')
