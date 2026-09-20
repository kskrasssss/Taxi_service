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



    def pages(self, page_size: int) -> FleetPages:
        return FleetPages(self, page_size)

    _CRITERIA = ("min_rating", "rider")

    def __call__(self, **criteria) -> Fleet:
        unknown = set(criteria) - set(self._CRITERIA)
        if unknown:
            raise TypeError(
                f"невідомі критерії: {', '.join(sorted(unknown))}. "
                f"Припустимі: {', '.join(self._CRITERIA)}"
            )
        min_rating = criteria.get("min_rating")
        rider = criteria.get("rider")
        return Fleet(
            r for r in self._rides
            if (min_rating is None or r.rating >= min_rating)
            and (rider is None or r.rider == rider)
        )

    def get(self, ride_id: str) -> Ride:
        try:
            return self._index[ride_id]
        except KeyError:
            raise EntityNotFound(ride_id) from None
    


class FleetPages:
    """Ітератор посторінкового обходу Fleet."""

    def __init__(self, fleet: Fleet, page_size: int) -> None:
        if page_size <= 0:
            raise ValueError("розмір сторінки повинен бути додатним")
        self._fleet = fleet          # посилання, без копіювання
        self._page_size = page_size
        self._pos = 0

    def __iter__(self) -> FleetPages:
        return self

    def __next__(self) -> list[Ride]:
        if self._pos >= len(self._fleet):
            raise StopIteration
        page = list(self._fleet[self._pos:self._pos + self._page_size])
        self._pos += self._page_size
        return page