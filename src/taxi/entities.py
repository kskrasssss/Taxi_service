from __future__ import annotations

import re
from typing import Any


class Ride:
    """Поїздка таксі."""

    # регулярний вираз на рівні класу: "R-" плюс одна чи більше цифр
    _ID_RE = re.compile(r"^R-\d+$")

    def __init__(self, ride_id: str, rider: str, distance_km: float,
                 fare: float, rating: int) -> None:
        # перевірка id тут же, у конструкторі — статичний метод не потребує self/cls, тож викликаємо і так, і так
        if not self.is_valid_ride_id(ride_id):
            raise ValueError("ідентифікатор поїздки повинен мати вигляд 'R-<число>'")
        self._ride_id = ride_id          # ride_id лише для читання, тому пишемо в _ride_id напряму, не через сетер
        # решта полів — через ЙОГО Ж property-сетери нижче, тому валідація спрацьовує вже тут, у конструкторі
        self.rider = rider
        self.distance_km = distance_km
        self.fare = fare
        self.rating = rating

    @property
    def ride_id(self) -> str:
        # гетер без сетера -> поле фактично тільки для читання ззовні
        return self._ride_id

    @property
    def rider(self) -> str:
        return self._rider

    @rider.setter
    def rider(self, value: str) -> None:
        # value.strip() перевіряє, що рядок не складається лише з пробілів
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ім'я пасажира не може бути порожнім")
        self._rider = value   # ВАЖЛИВО: пишемо в self._rider, а не self.rider — інакше нескінченна рекурсія

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
        # isinstance(value, bool) виключаємо окремо: bool — підклас int, True/False інакше пройшли б як 1/0
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError("рейтинг повинен бути цілим числом від 1 до 5")
        self._rating = value

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ride:
        # cls - сам клас Ride (або підклас, якщо колись з'явиться). cls(...) викликає звичайний __init__,
        # тому валідація полів спрацьовує автоматично, дублювати перевірки тут не треба
        try:
            return cls(
                ride_id=data["ride_id"],
                rider=data["rider"],
                distance_km=data["distance_km"],
                fare=data["fare"],
                rating=data["rating"],
            )
        except KeyError as e:
            # перетворюємо "технічний" KeyError на змістовний ValueError; from None ховає внутрішній ланцюжок
            raise ValueError(f"у словнику відсутнє поле {e}") from None

    @staticmethod
    def is_valid_ride_id(value: str) -> bool:
        # немає ні self, ні cls - це проста функція, покладена в клас для порядку.
        # Може бути викликана і Ride.is_valid_ride_id(...), і self.is_valid_ride_id(...) (як у __init__)
        return isinstance(value, str) and bool(Ride._ID_RE.match(value))

    def __repr__(self) -> str:
        return (f"Ride(ride_id={self._ride_id!r}, rider={self._rider!r}, "
                f"distance_km={self._distance_km}, fare={self._fare}, "
                f"rating={self._rating})")