from __future__ import annotations

from functools import total_ordering
from typing import Any

from dataclasses import dataclass

@total_ordering
class GeoPoint:
    """Незмінна географічна координата (широта, довгота)."""

    __slots__ = ("lat", "lon", "_frozen")

    def __init__(self, lat: float, lon: float) -> None:
        if not -90 <= lat <= 90:
            raise ValueError("широта повинна бути в межах [-90, 90]")
        if not -180 <= lon <= 180:
            raise ValueError("довгота повинна бути в межах [-180, 180]")
        object.__setattr__(self, "lat", lat)
        object.__setattr__(self, "lon", lon)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError("об'єкт GeoPoint незмінний")
        object.__setattr__(self, name, value)

    def _key(self) -> tuple[float, float]:
        return (self.lat, self.lon)

    def __repr__(self) -> str:
        return f"GeoPoint(lat={self.lat}, lon={self.lon})"

    def __str__(self) -> str:
        ns = "N" if self.lat >= 0 else "S"
        ew = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat)}°{ns}, {abs(self.lon)}°{ew}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())


    def __add__(self, other: object) -> GeoPoint:
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return GeoPoint(self.lat + other.lat, self.lon + other.lon)

    def __sub__(self, other: object) -> GeoPoint:
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return GeoPoint(self.lat - other.lat, self.lon - other.lon)

    def __mul__(self, k: object) -> GeoPoint:
        if isinstance(k, bool) or not isinstance(k, (int, float)):
            return NotImplemented
        return GeoPoint(self.lat * k, self.lon * k)

    __rmul__ = __mul__

@dataclass(frozen=True, slots=True, order=True)
class GeoPointDC:
    """Та сама поведінка, але через dataclass."""

    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not -90 <= self.lat <= 90:
            raise ValueError("широта повинна бути в межах [-90, 90]")
        if not -180 <= self.lon <= 180:
            raise ValueError("довгота повинна бути в межах [-180, 180]")

    def __str__(self) -> str:
        ns = "N" if self.lat >= 0 else "S"
        ew = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat)}°{ns}, {abs(self.lon)}°{ew}"