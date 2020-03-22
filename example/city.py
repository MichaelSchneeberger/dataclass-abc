from abc import ABC

from example.mixins.citynamemixin import CityNameMixin
from example.mixins.spherepositionmixin import SpherePositionMixin


class City(CityNameMixin, SpherePositionMixin, ABC):
    pass
