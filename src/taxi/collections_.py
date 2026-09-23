from __future__ import annotations

from typing import Iterable, Iterator

from .decorators import validated
from .entities import Ride
from .errors import DuplicateEntity, EntityNotFound


class Fleet:
    """Колекція поїздок."""

    # дозволені імена критеріїв для __call__ — звіряємось із цим списком, щоб ловити помилки в запитах
    _CRITERIA = ("min_rating", "rider")

    def __init__(self, rides: Iterable[Ride] = ()) -> None:
        self._rides: list[Ride] = []       # список — тримає порядок, потрібен для __getitem__ з індексом/зрізом
        self._index: dict[str, Ride] = {}  # словник ride_id -> Ride — потрібен для швидкого get() і __contains__
        for ride in rides:
            self._append(ride)

    def _append(self, ride: Ride) -> None:
        # приватний хелпер (з підкресленням): додає одну поїздку одразу в обидві структури й пильнує дублікати
        if ride.ride_id in self._index:
            raise DuplicateEntity(ride.ride_id)
        self._rides.append(ride)
        self._index[ride.ride_id] = ride

    def __len__(self) -> int:
        # викликається через len(fleet)
        return len(self._rides)

    def __getitem__(self, key: int | slice) -> Ride | Fleet:
        # викликається через fleet[0] або fleet[0:2]
        if isinstance(key, slice):
            # для зрізу повертаємо НОВИЙ Fleet (не list!), щоб результат лишався повноцінною колекцією
            return Fleet(self._rides[key])
        return self._rides[key]

    def __contains__(self, item: object) -> bool:
        # викликається через "x in fleet". Приймає і рядок id, і сам об'єкт Ride
        ride_id = item.ride_id if isinstance(item, Ride) else item
        return ride_id in self._index   # пошук у словнику — швидкий, О(1)

    def __iter__(self) -> Iterator[Ride]:
        # викликається на початку "for ride in fleet"; кожен виклик дає новий незалежний ітератор
        return iter(self._rides)

    def __repr__(self) -> str:
        return f"Fleet({self._rides!r})"

    def pages(self, page_size: int) -> FleetPages:
        # повертає окремий об'єкт-ітератор (клас нижче), а не список сторінок одразу
        return FleetPages(self, page_size)

    def __call__(self, **criteria) -> Fleet:
        # викликається через fleet(min_rating=4, rider="Іван") — об'єкт поводиться як функція
        unknown = set(criteria) - set(self._CRITERIA)
        if unknown:
            raise TypeError(
                f"невідомі критерії: {', '.join(sorted(unknown))}. "
                f"Припустимі: {', '.join(self._CRITERIA)}"
            )
        min_rating = criteria.get("min_rating")   # None, якщо критерій не передали
        rider = criteria.get("rider")
        return Fleet(
            r for r in self._rides
            if (min_rating is None or r.rating >= min_rating)  # діапазонний критерій
            and (rider is None or r.rider == rider)             # критерій за рівністю
        )

    def get(self, ride_id: str) -> Ride:
        # стиль EAFP: спершу пробуємо, а не перевіряємо "if ride_id in self._index" заздалегідь (це LBYL)
        try:
            return self._index[ride_id]
        except KeyError:
            # from None ховає технічний KeyError, лишаючи лише наш доменний виняток у трасуванні
            raise EntityNotFound(ride_id) from None

    def __add__(self, other: object) -> Fleet:
        # викликається через fleet_a + fleet_b
        if not isinstance(other, Fleet):
            return NotImplemented   # НЕ підіймаємо TypeError самі — даємо Python шанс спробувати інший бік
        merged = Fleet(self._rides)   # копія списку self, новий Fleet
        for ride in other:
            if ride.ride_id not in merged._index:   # без дублікатів за id
                merged._append(ride)
        return merged

    def __radd__(self, other: object) -> Fleet:
        # викликається, коли ЛІВИЙ операнд не вміє додавати Fleet — головний кейс: sum([a, b, c])
        # sum починає з 0 і робить "0 + a", тому other тут спочатку буде 0
        if other == 0:
            return Fleet(self._rides)   # копія поточної колекції
        return self.__add__(other)      # інші випадки — звичайне додавання (тут other вже праворуч)

    @validated(ride_id="non_empty", rider="non_empty", distance_km="positive",
               fare="positive", rating="one_of:1,2,3,4,5")
    # декоратор перевіряє іменовані аргументи ЩЕ ДО виконання тіла методу
    def add_ride(self, *, ride_id: str, rider: str, distance_km: float,
                 fare: float, rating: int) -> Ride:
        ride = Ride(ride_id, rider, distance_km, fare, rating)  # тут спрацює ще й валідація з entities.py
        self._append(ride)
        return ride

    @validated(old="non_empty", new="non_empty")
    def rename_rider(self, *, old: str, new: str) -> int:
        # перейменовує пасажира в усіх поїздках, де він зустрічається; повертає скільки поїздок змінено
        count = 0
        for ride in self._rides:
            if ride.rider == old:
                ride.rider = new   # це знову йде через сетер rider, тобто теж валідується
                count += 1
        return count


class FleetPages:
    """Ітератор посторінкового обходу Fleet."""

    def __init__(self, fleet: Fleet, page_size: int) -> None:
        if page_size <= 0:
            raise ValueError("розмір сторінки повинен бути додатним")
        self._fleet = fleet          # ПОСИЛАННЯ на живу колекцію, елементи НЕ копіюються
        self._page_size = page_size
        self._pos = 0                # поточна позиція обходу

    def __iter__(self) -> FleetPages:
        # ітератор повертає сам себе — так і має бути за протоколом ітератора
        return self

    def __next__(self) -> list[Ride]:
        # викликається на кожному кроці "for page in fleet.pages(2)"
        if self._pos >= len(self._fleet):
            raise StopIteration   # сигнал "елементи закінчились", for сам його ловить і завершує цикл
        page = list(self._fleet[self._pos:self._pos + self._page_size])  # бере зріз через __getitem__ колекції
        self._pos += self._page_size
        return page