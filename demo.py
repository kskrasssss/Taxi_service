import sys
from pathlib import Path

# без цього рядка "from taxi import ..." нижче не спрацював би - пакет лежить у src/, а не в корені
sys.path.insert(0, str(Path(__file__).parent / "src"))

from taxi import DispatchSession, Fleet, GeoPoint, GeoPointDC, Ride


def section(title: str) -> None:
    # просто друкує заголовок розділу для наочності у консолі
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def attempt(label: str, fn) -> None:
    # виконує fn(); якщо впав виняток — друкує його тип і повідомлення й НЕ падає сама
    try:
        fn()
    except Exception as e:
        print(f"  {label}: {type(e).__name__}: {e}")
    else:
        print(f"  {label}: !!! ПОМИЛКИ НЕ БУЛО !!!")   # сигнал, що там, де очікувалась помилка, її не було


def make_rides() -> list[Ride]:
    # тестові дані, однакові для декількох демонстрацій
    return [
        Ride("R-1001", "Іван", 5.2, 120, 5),
        Ride("R-1002", "Марія", 12.0, 300, 4),
        Ride("R-1003", "Іван", 3.1, 80, 3),
        Ride("R-1004", "Олена", 20.0, 500, 5),
        Ride("R-1005", "Петро", 7.5, 150, 2),
    ]


def demo_task1() -> None:
    section("Завдання 1. Об'єкт-значення GeoPoint")
    for cls in (GeoPoint, GeoPointDC):   # той самий сценарій для обох реалізацій
        print(f"\n-- {cls.__name__} --")
        a, b = cls(50.45, 30.52), cls(50.45, 30.52)   # два РІЗНІ об'єкти з ОДНАКОВИМ вмістом
        print("a is b:", a is b)      # False — різні об'єкти в пам'яті
        print("a == b:", a == b)      # True — рівність за вмістом (__eq__)
        print("repr:", repr(a), "| str:", str(a))
        print("set:", {a, b}, "-> розмір", len({a, b}))   # 1 елемент — бо hash і eq узгоджені
        d = {a: "Київ"}
        print("dict[b]:", d[b])       # знайшли за РІЗНИМ, але РІВНИМ об'єктом
        pts = [cls(10, 20), cls(-5, 3), cls(10, 5)]
        print("sorted:", [str(p) for p in sorted(pts)])   # працює завдяки __lt__ / total_ordering
        print("a == 5:", a == 5)      # порівняння з чужим типом -> False (через NotImplemented)
        attempt("a.lat = 0", lambda: setattr(a, "lat", 0))       # AttributeError: незмінний
        attempt("a.foo = 1", lambda: setattr(a, "foo", 1))       # AttributeError/TypeError: нового поля немає
        attempt("a < 5", lambda: a < 5)                          # TypeError: непорівнюваний тип


def demo_task2() -> None:
    section("Завдання 2. Сутність Ride")
    r = Ride("R-2001", "Іван", 5.2, 120, 5)
    print("Коректна:", r)

    print("\n-- у конструкторі --")
    # для кожного обмеження — по одному прикладу порушення, ще на етапі створення об'єкта
    attempt("distance_km=0", lambda: Ride("R-1", "Іван", 0, 100, 5))
    attempt("fare=-5", lambda: Ride("R-1", "Іван", 5, -5, 5))
    attempt("rating=0", lambda: Ride("R-1", "Іван", 5, 100, 0))
    attempt("rating=6", lambda: Ride("R-1", "Іван", 5, 100, 6))
    attempt("rider=''", lambda: Ride("R-1", "  ", 5, 100, 5))
    attempt("ride_id='X1'", lambda: Ride("X1", "Іван", 5, 100, 5))

    print("\n-- при присвоєнні --")
    # ті самі перевірки, але вже на готовому об'єкті - доводить, що валідація в сетерах, а не лише в __init__
    attempt("r.distance_km = -1", lambda: setattr(r, "distance_km", -1))
    attempt("r.fare = 0", lambda: setattr(r, "fare", 0))
    attempt("r.rating = 7", lambda: setattr(r, "rating", 7))
    attempt("r.rider = ''", lambda: setattr(r, "rider", ""))
    r.rating = 4   # коректне присвоєння — проходить без винятку
    print("r.rating = 4 -> ок:", r.rating)

    print("\n-- from_dict --")
    good = {"ride_id": "R-3", "rider": "Марія", "distance_km": 3, "fare": 90, "rating": 4}
    print("коректний:", Ride.from_dict(good))
    attempt("некоректний", lambda: Ride.from_dict({**good, "rating": 9}))   # {**good, ...} - копія словника зі зміненим полем
    attempt("неповний", lambda: Ride.from_dict({"ride_id": "R-4"}))         # бракує полів -> ValueError

    print("\n-- is_valid_ride_id --")
    for v in ("R-1001", "R-", "1001", "r-5"):
        print(f"  {v!r}: {Ride.is_valid_ride_id(v)}")   # виклик через клас, без створення Ride


def demo_task3() -> None:
    section("Завдання 3. Колекція Fleet")
    fleet = Fleet(make_rides())
    print("len:", len(fleet))                    # __len__
    print("fleet[0]:", fleet[0])                  # __getitem__ з int
    sl = fleet[0:2]
    print("fleet[0:2] тип:", type(sl).__name__, "->", sl)   # __getitem__ зі slice -> новий Fleet, не list
    print("R-1002 in fleet:", "R-1002" in fleet, "| fleet[1] in fleet:", fleet[1] in fleet)  # __contains__, обидва варіанти
    print("R-9999 in fleet:", "R-9999" in fleet)
    print("for:")
    for ride in fleet:                            # __iter__
        print("  ", ride)

    print("\n-- pages(2) --")
    for i, page in enumerate(fleet.pages(2), 1):  # pages() -> FleetPages -> __next__ по колу
        print(f"  сторінка {i}: {[r.ride_id for r in page]}")   # остання сторінка неповна — і це нормально

    print("\n-- запити через __call__ --")
    print("min_rating=4:", [r.ride_id for r in fleet(min_rating=4)])   # fleet(...) викликає __call__
    print("rider='Іван':", [r.ride_id for r in fleet(rider="Іван")])
    print("обидва:", [r.ride_id for r in fleet(min_rating=4, rider="Іван")])
    attempt("fleet(colour='x')", lambda: fleet(colour="x"))            # невідомий критерій -> TypeError

    print("\n-- get (EAFP) --")
    print("get('R-1003'):", fleet.get("R-1003"))
    attempt("get('R-9999')", lambda: fleet.get("R-9999"))              # EntityNotFound


def demo_task4_fleet() -> None:
    section("Завдання 4. Оператори над Fleet")
    fleet = Fleet(make_rides())
    f1, f2, f3 = fleet[0:2], fleet[1:4], fleet[3:5]   # зрізи перетинаються - R-1002 в f1 і f2 одночасно
    print("f1:", [r.ride_id for r in f1])
    print("f2:", [r.ride_id for r in f2])
    print("f1 + f2:", [r.ride_id for r in f1 + f2], "(без дублікатів)")   # __add__ прибирає повтор R-1002
    total = sum([f1, f2, f3])   # sum -> 0 + f1 (спрацьовує __radd__ з other=0) -> потім звичайні __add__
    print("sum:", [r.ride_id for r in total], "| тип:", type(total).__name__)
    attempt("f1 + 5", lambda: f1 + 5)   # __add__ повертає NotImplemented -> Python сам кидає TypeError
    attempt("5 + f1", lambda: 5 + f1)   # 5.__add__(f1) не вміє -> f1.__radd__(5) -> not (5==0) -> __add__(5) -> NotImplemented -> TypeError


def demo_task4_geopoint() -> None:
    p, q = GeoPoint(10, 20), GeoPoint(5, 5)
    print("\n-- арифметика GeoPoint --")
    print("p + q:", repr(p + q))
    print("p - q:", repr(p - q))
    print("p * 2:", repr(p * 2))    # __mul__
    print("2 * p:", repr(2 * p))    # __rmul__ (int не вміє множити на GeoPoint, тому крутиться в інший бік)
    attempt("p + 10", lambda: p + 10)   # чужий тип -> NotImplemented -> TypeError
    attempt("GeoPoint(80,0) + GeoPoint(20,0)", lambda: GeoPoint(80, 0) + GeoPoint(20, 0))  # 100° > 90° -> ValueError у __init__
    pts = [GeoPoint(10, 20), GeoPoint(-5, 3), GeoPoint(10, 5)]
    print("min:", min(pts), "| max:", max(pts))   # працює завдяки __lt__/total_ordering
    print("sorted:", [str(x) for x in sorted(pts)])


def demo_task5() -> None:
    section("Завдання 5. Декоратор validated")
    fleet = Fleet()
    ok = dict(ride_id="R-1", rider="Іван", distance_km=5, fare=100, rating=5)
    print("коректно:", fleet.add_ride(**ok))
    # для кожного правила — по одному порушенню; {**ok, "поле": погане_значення} — копія словника зі зміненим полем
    attempt("positive (distance_km=0)", lambda: fleet.add_ride(**{**ok, "ride_id": "R-2", "distance_km": 0}))
    attempt("positive (fare=-1)", lambda: fleet.add_ride(**{**ok, "ride_id": "R-2", "fare": -1}))
    attempt("non_empty (rider='  ')", lambda: fleet.add_ride(**{**ok, "ride_id": "R-2", "rider": "  "}))
    attempt("one_of (rating=9)", lambda: fleet.add_ride(**{**ok, "ride_id": "R-2", "rating": 9}))
    print("rename_rider:", fleet.rename_rider(old="Іван", new="Іванко"), "поїздка(и)")
    attempt("rename_rider(new='')", lambda: fleet.rename_rider(old="Іванко", new=""))
    print("Fleet.add_ride.__name__ =", Fleet.add_ride.__name__)   # "add_ride", а не "wrapper" — доказ functools.wraps


def demo_task6() -> None:
    section("Завдання 6. DispatchSession")
    fleet = Fleet(make_rides()[:2])
    print("до:", [r.ride_id for r in fleet])

    with DispatchSession(fleet) as s:   # __enter__: знімок зроблено, s — це той самий fleet
        s.add_ride(ride_id="R-7001", rider="Анна", distance_km=4, fare=90, rating=5)
        s.add_ride(ride_id="R-7002", rider="Богдан", distance_km=6, fare=110, rating=4)
    # __exit__ без винятку -> зміни лишаються
    print("після успішного сеансу:", [r.ride_id for r in fleet])

    before = [r.ride_id for r in fleet]
    try:
        with DispatchSession(fleet) as s:
            s.add_ride(ride_id="R-8001", rider="Х", distance_km=1, fare=50, rating=3)
            s.rename_rider(old="Іван", new="ЗМІНЕНО")   # часткова зміна ДО винятку - теж має відкотитись
            s.add_ride(ride_id="R-8002", rider="Y", distance_km=2, fare=60, rating=4)
            raise RuntimeError("збій під час сеансу")   # __exit__ побачить цей виняток і зробить відкат
    except RuntimeError as e:
        print("виняток дійшов до main:", e)   # доказ, що __exit__ повернув False, а не проковтнув помилку
    print("до блоку :", before)
    print("після    :", [r.ride_id for r in fleet])
    print("стан збігається:", before == [r.ride_id for r in fleet])   # True -> відкат спрацював
    print("ім'я 'Іван' відновлено:", fleet.get("R-1001").rider)       # доказ, що й rename_rider теж відкотився


def main() -> None:
    demo_task1()
    demo_task2()
    demo_task3()
    demo_task4_fleet()
    demo_task4_geopoint()
    demo_task5()
    demo_task6()


if __name__ == "__main__":
    main()