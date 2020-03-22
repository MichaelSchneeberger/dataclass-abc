from abc import ABC

from example.city import City
from example.mixins.countrynamemixin import CountryNameMixin


class CapitalCity(CountryNameMixin, City, ABC):
    pass
