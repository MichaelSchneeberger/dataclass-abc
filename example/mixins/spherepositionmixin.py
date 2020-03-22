from abc import ABC, abstractmethod
from math import radians, sin, cos, asin, sqrt


class SpherePositionMixin(ABC):
    @property
    @abstractmethod
    def lon(self) -> float:
        ...

    @property
    @abstractmethod
    def lat(self) -> float:
        ...

    def distance_to(
            self,
            other: 'SpherePositionMixin',
    ) -> float:

        r = 6371  # Earth radius in kilometers
        lam_1, lam_2 = radians(self.lon), radians(other.lon)
        phi_1, phi_2 = radians(self.lat), radians(other.lat)
        h = (sin((phi_2 - phi_1) / 2)**2
             + cos(phi_1) * cos(phi_2) * sin((lam_2 - lam_1) / 2)**2)
        return 2 * r * asin(sqrt(h))
