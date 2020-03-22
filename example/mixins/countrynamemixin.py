from abc import ABC, abstractmethod


class CountryNameMixin(ABC):
    @property
    @abstractmethod
    def country_name(self) -> str:
        ...
