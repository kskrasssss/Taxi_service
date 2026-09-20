import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from taxi import GeoPoint, GeoPointDC


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


if __name__ == "__main__":
    main()