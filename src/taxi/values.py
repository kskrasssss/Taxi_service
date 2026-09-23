from __future__ import annotations  # дозволяє писати "GeoPoint" як тип у методах самого GeoPoint (клас ще не оголошений, коли Python читає анотації)

from dataclasses import dataclass
from functools import total_ordering  # декоратор, що добудовує <=, >, >= маючи __eq__ і __lt__
from typing import Any


@total_ordering  # бере __eq__ і __lt__ нижче й сам генерує __le__, __gt__, __ge__
class GeoPoint:
    """Незмінна географічна координата (широта, довгота)."""

    # __slots__ забороняє додавати екземпляру будь-які атрибути, крім перелічених.
    # Побічний ефект: у екземпляра немає __dict__, і "a.foo = 1" впаде.
    __slots__ = ("lat", "lon", "_frozen")

    def __init__(self, lat: float, lon: float) -> None:
        # валідація діапазону координат — тут же "заодно" ловимо некоректну арифметику з __add__/__mul__
        if not -90 <= lat <= 90:
            raise ValueError("широта повинна бути в межах [-90, 90]")
        if not -180 <= lon <= 180:
            raise ValueError("довгота повинна бути в межах [-180, 180]")
        # object.__setattr__ — це "прямий" виклик базового присвоєння в ОБХІД нашого __setattr__ нижче.
        # Якби писали просто self.lat = lat, спрацював би наш __setattr__ і ще до появи _frozen все було б ок,
        # але це заплутано, тож для чистоти конструктор завжди пише через object.__setattr__.
        object.__setattr__(self, "lat", lat)
        object.__setattr__(self, "lon", lon)
        # прапорець "конструктор завершив роботу" — з цього моменту об'єкт заморожений
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        # Python викликає цей метод при КОЖНОМУ "obj.attr = value", включно з тими, що всередині __init__.
        # getattr(..., False) — дефолт на випадок, коли _frozen ще не існує (на самому початку __init__)
        if getattr(self, "_frozen", False):
            raise AttributeError("об'єкт GeoPoint незмінний")
        object.__setattr__(self, name, value)

    def _key(self) -> tuple[float, float]:
        # допоміжний "ключ" для порівняння і хешування — щоб не дублювати (lat, lon) у трьох місцях
        return (self.lat, self.lon)

    def __repr__(self) -> str:
        # подання для розробника / відладки: придатне для відтворення об'єкта
        return f"GeoPoint(lat={self.lat}, lon={self.lon})"

    def __str__(self) -> str:
        # подання для кінцевого користувача, викликається через str(obj) або print(obj)
        ns = "N" if self.lat >= 0 else "S"
        ew = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat)}°{ns}, {abs(self.lon)}°{ew}"

    def __eq__(self, other: object) -> bool:
        # чужий тип -> NotImplemented (не False!), щоб Python дав шанс іншому операнду / сам вирішив
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        # разом з @total_ordering цього достатньо, щоб отримати <=, >, >= безкоштовно
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        # ОБОВ'ЯЗКОВО той самий "ключ", що й у __eq__ — інакше a == b, але hash(a) != hash(b), і set/dict ламаються
        return hash(self._key())

    def __add__(self, other: object) -> GeoPoint:
        # a + b: трактуємо як зсув координат; несумісний тип -> NotImplemented, а не власний TypeError
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return GeoPoint(self.lat + other.lat, self.lon + other.lon)  # тут же і валідація діапазону через __init__

    def __sub__(self, other: object) -> GeoPoint:
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return GeoPoint(self.lat - other.lat, self.lon - other.lon)

    def __mul__(self, k: object) -> GeoPoint:
        # a * число: масштабування координат. isinstance(k, bool) виключено окремо,
        # бо bool — підклас int, і True/False інакше тихо пройшли б як 1/0
        if isinstance(k, bool) or not isinstance(k, (int, float)):
            return NotImplemented
        return GeoPoint(self.lat * k, self.lon * k)

    # __rmul__ потрібен для "2 * point": Python спершу пробує int.__mul__(2, point),
    # той не вміє й повертає NotImplemented, тоді Python пробує point.__rmul__(2)
    __rmul__ = __mul__


@dataclass(frozen=True, slots=True, order=True)
# frozen=True -> забороняє присвоєння полям (як наш __setattr__, тільки готове з коробки)
# slots=True -> те саме, що ручний __slots__ вище
# order=True -> dataclass сам згенерує __lt__/__le__/__gt__/__ge__ за порядком полів (lat, потім lon)
class GeoPointDC:
    """Та сама поведінка, але через dataclass."""

    lat: float
    lon: float
    # __init__, __repr__, __eq__, __hash__ dataclass згенерував сам за цими двома полями

    def __post_init__(self) -> None:
        # викликається автоматично одразу після згенерованого __init__ — сюди кладемо власну валідацію,
        # бо dataclass не вміє перевіряти діапазони сам
        if not -90 <= self.lat <= 90:
            raise ValueError("широта повинна бути в межах [-90, 90]")
        if not -180 <= self.lon <= 180:
            raise ValueError("довгота повинна бути в межах [-180, 180]")

    def __str__(self) -> str:
        # dataclass сам не генерує __str__ (лише __repr__), тому пишемо вручну, як у ручній версії
        ns = "N" if self.lat >= 0 else "S"
        ew = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat)}°{ns}, {abs(self.lon)}°{ew}"