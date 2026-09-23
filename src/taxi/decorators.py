import functools
import inspect
from typing import Any, Callable


def _check(name: str, value: Any, rule: str) -> None:
    # приватна функція-хелпер: перевіряє ОДНЕ значення за ОДНИМ правилом
    if rule == "positive":
        # isinstance(value, bool) виключено окремо — bool є підкласом int
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"аргумент '{name}': правило positive порушено (отримано {value!r})")
    elif rule == "non_empty":
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"аргумент '{name}': правило non_empty порушено (отримано {value!r})")
    elif rule.startswith("one_of:"):
        allowed = rule.split(":", 1)[1].split(",")   # "one_of:1,2,3" -> ["1","2","3"]
        if str(value) not in allowed:   # порівнюємо як рядки, бо rating — int, а allowed — рядки
            raise ValueError(f"аргумент '{name}': правило {rule} порушено (отримано {value!r})")
    else:
        raise ValueError(f"невідоме правило {rule!r} для аргумента '{name}'")


def validated(**rules: str) -> Callable:
    # РІВЕНЬ 1: приймає правила виду ride_id="non_empty", rating="one_of:1,2,3,4,5"
    # і "запам'ятовує" їх у замиканні для decorator нижче
    def decorator(func: Callable) -> Callable:
        # РІВЕНЬ 2: приймає САМУ функцію (наприклад, add_ride) і повертає її обгортку
        sig = inspect.signature(func)   # "підпис" функції — потрібен, щоб зіставити позиційні/іменовані аргументи з іменами параметрів

        @functools.wraps(func)   # копіює __name__, __doc__ і т.д. з func на wrapper — без цього ім'я стало б "wrapper"
        def wrapper(*args, **kwargs):
            # РІВЕНЬ 3: викликається кожного разу, коли хтось насправді кличе декоровану функцію
            bound = sig.bind(*args, **kwargs)   # зв'язує передані значення з іменами параметрів (враховує і self)
            for name, rule in rules.items():
                if name in bound.arguments:
                    _check(name, bound.arguments[name], rule)
            return func(*args, **kwargs)   # усе гаразд -> викликаємо оригінальну функцію без змін

        return wrapper

    return decorator