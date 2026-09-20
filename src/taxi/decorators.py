import functools
import inspect
from typing import Any, Callable


def _check(name: str, value: Any, rule: str) -> None:
    if rule == "positive":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"аргумент '{name}': правило positive порушено (отримано {value!r})")
    elif rule == "non_empty":
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"аргумент '{name}': правило non_empty порушено (отримано {value!r})")
    elif rule.startswith("one_of:"):
        allowed = rule.split(":", 1)[1].split(",")
        if str(value) not in allowed:
            raise ValueError(f"аргумент '{name}': правило {rule} порушено (отримано {value!r})")
    else:
        raise ValueError(f"невідоме правило {rule!r} для аргумента '{name}'")


def validated(**rules: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            for name, rule in rules.items():
                if name in bound.arguments:
                    _check(name, bound.arguments[name], rule)
            return func(*args, **kwargs)

        return wrapper

    return decorator