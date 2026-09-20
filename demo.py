import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from taxi import GeoPoint, GeoPointDC,  Ride, Fleet


def section(title: str) -> None:
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def attempt(label: str, fn) -> None:
    """Виконує fn і друкує перехоплений виняток."""
    try:
        fn()
    except Exception as e:
        print(f"  {label}: {type(e).__name__}: {e}")
    else:
        print(f"  {label}: !!! ПОМИЛКИ НЕ БУЛО !!!")


def demo_task1() -> None:
    section("Завдання 1. Об'єкт-значення GeoPoint")
    for cls in (GeoPoint, GeoPointDC):
        print(f"\n-- {cls.__name__} --")
        a, b = cls(50.45, 30.52), cls(50.45, 30.52)
        print("a is b:", a is b)
        print("a == b:", a == b)
        print("repr:", repr(a), "| str:", str(a))
        print("set:", {a, b}, "-> розмір", len({a, b}))
        d = {a: "Київ"}
        print("dict[b]:", d[b])
        pts = [cls(10, 20), cls(-5, 3), cls(10, 5)]
        print("sorted:", [str(p) for p in sorted(pts)])
        print("a == 5:", a == 5)
        attempt("a.lat = 0", lambda: setattr(a, "lat", 0))
        attempt("a.foo = 1", lambda: setattr(a, "foo", 1))
        attempt("a < 5", lambda: a < 5)


def main() -> None:
    demo_task1()

def make_rides() -> list[Ride]:
    return [
        Ride("R-1001", "Іван", 5.2, 120, 5),
        Ride("R-1002", "Марія", 12.0, 300, 4),
        Ride("R-1003", "Іван", 3.1, 80, 3),
        Ride("R-1004", "Олена", 20.0, 500, 5),
        Ride("R-1005", "Петро", 7.5, 150, 2),
    ]


def demo_task2() -> None:
    section("Завдання 2. Сутність Ride")
    r = Ride("R-2001", "Іван", 5.2, 120, 5)
    print("Коректна:", r)

    print("\n-- у конструкторі --")
    attempt("distance_km=0", lambda: Ride("R-1", "Іван", 0, 100, 5))
    attempt("fare=-5", lambda: Ride("R-1", "Іван", 5, -5, 5))
    attempt("rating=0", lambda: Ride("R-1", "Іван", 5, 100, 0))
    attempt("rating=6", lambda: Ride("R-1", "Іван", 5, 100, 6))
    attempt("rider=''", lambda: Ride("R-1", "  ", 5, 100, 5))
    attempt("ride_id='X1'", lambda: Ride("X1", "Іван", 5, 100, 5))

    print("\n-- при присвоєнні --")
    attempt("r.distance_km = -1", lambda: setattr(r, "distance_km", -1))
    attempt("r.fare = 0", lambda: setattr(r, "fare", 0))
    attempt("r.rating = 7", lambda: setattr(r, "rating", 7))
    attempt("r.rider = ''", lambda: setattr(r, "rider", ""))
    r.rating = 4
    print("r.rating = 4 -> ок:", r.rating)

    print("\n-- from_dict --")
    good = {"ride_id": "R-3", "rider": "Марія", "distance_km": 3, "fare": 90, "rating": 4}
    print("коректний:", Ride.from_dict(good))
    attempt("некоректний", lambda: Ride.from_dict({**good, "rating": 9}))
    attempt("неповний", lambda: Ride.from_dict({"ride_id": "R-4"}))

    print("\n-- is_valid_ride_id --")
    for v in ("R-1001", "R-", "1001", "r-5"):
        print(f"  {v!r}: {Ride.is_valid_ride_id(v)}")



def demo_task3() -> None:
    section("Завдання 3. Колекція Fleet")
    fleet = Fleet(make_rides())
    print("len:", len(fleet))
    print("fleet[0]:", fleet[0])
    sl = fleet[0:2]
    print("fleet[0:2] тип:", type(sl).__name__, "->", sl)
    print("R-1002 in fleet:", "R-1002" in fleet, "| fleet[1] in fleet:", fleet[1] in fleet)
    print("R-9999 in fleet:", "R-9999" in fleet)
    print("for:")
    for ride in fleet:
        print("  ", ride)

if __name__ == "__main__":
    main()