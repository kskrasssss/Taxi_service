from __future__ import annotations

from typing import Iterable, Iterator

from .entities import Ride
from .errors import DuplicateEntity, EntityNotFound


class Fleet:
    """Колекція поїздок."""

    def __init__(self, rides: Iterable[Ride] = ()) -> None:
        self._rides: list[Ride] = []
        self._index: dict[str, Ride] = {}
        for ride in rides:
            self._append(ride)

    def _append(self, ride: Ride) -> None:
        if ride.ride_id in self._index:
            raise DuplicateEntity(ride.ride_id)
        self._rides.append(ride)
        self._index[ride.ride_id] = ride

    def __len__(self) -> int:
        return len(self._rides)

    def __getitem__(self, key: int | slice) -> Ride | Fleet:
        if isinstance(key, slice):
            return Fleet(self._rides[key])
        return self._rides[key]

    def __contains__(self, item: object) -> bool:
        ride_id = item.ride_id if isinstance(item, Ride) else item
        return ride_id in self._index

    def __iter__(self) -> Iterator[Ride]:
        return iter(self._rides)

    def __repr__(self) -> str:
        return f"Fleet({self._rides!r})"