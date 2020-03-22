from abc import ABC, abstractmethod


class CityNameMixin(ABC):
    @property
    @abstractmethod
    def city_name(self) -> str:
        ...
