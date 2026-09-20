from __future__ import annotations

import re
from typing import Any


class Ride:
    """Поїздка таксі."""

    _ID_RE = re.compile(r"^R-\d+$")

    def __init__(self, ride_id: str, rider: str, distance_km: float,
                 fare: float, rating: int) -> None:
        if not self.is_valid_ride_id(ride_id):
            raise ValueError("ідентифікатор поїздки повинен мати вигляд 'R-<число>'")
        self._ride_id = ride_id
        self.rider = rider              # усе йде через сетери
        self.distance_km = distance_km
        self.fare = fare
        self.rating = rating

    @property
    def ride_id(self) -> str:
        return self._ride_id

    @property
    def rider(self) -> str:
        return self._rider

    @rider.setter
    def rider(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ім'я пасажира не може бути порожнім")
        self._rider = value

    @property
    def distance_km(self) -> float:
        return self._distance_km

    @distance_km.setter
    def distance_km(self, value: float) -> None:
        if value <= 0:
            raise ValueError("відстань поїздки повинна бути додатною")
        self._distance_km = value

    @property
    def fare(self) -> float:
        return self._fare

    @fare.setter
    def fare(self, value: float) -> None:
        if value <= 0:
            raise ValueError("вартість поїздки повинна бути додатною")
        self._fare = value

    @property
    def rating(self) -> int:
        return self._rating

    @rating.setter
    def rating(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError("рейтинг повинен бути цілим числом від 1 до 5")
        self._rating = value

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ride:
        try:
            return cls(
                ride_id=data["ride_id"],
                rider=data["rider"],
                distance_km=data["distance_km"],
                fare=data["fare"],
                rating=data["rating"],
            )
        except KeyError as e:
            raise ValueError(f"у словнику відсутнє поле {e}") from None

    @staticmethod
    def is_valid_ride_id(value: str) -> bool:
        return isinstance(value, str) and bool(Ride._ID_RE.match(value))

    def __repr__(self) -> str:
        return (f"Ride(ride_id={self._ride_id!r}, rider={self._rider!r}, "
                f"distance_km={self._distance_km}, fare={self._fare}, "
                f"rating={self._rating})")