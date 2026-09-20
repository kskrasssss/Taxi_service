import copy
from types import TracebackType

from .collections_ import Fleet


class DispatchSession:
    """Атомарний пакет змін над Fleet: при винятку все відкочується."""

    def __init__(self, fleet: Fleet) -> None:
        self._fleet = fleet
        self._snapshot: Fleet | None = None

    def __enter__(self) -> Fleet:
        self._snapshot = copy.deepcopy(self._fleet)
        return self._fleet

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: TracebackType | None) -> bool:
        if exc_type is not None and self._snapshot is not None:
            self._fleet.__dict__.update(self._snapshot.__dict__)  # відновлення на місці
        self._snapshot = None
        return False  # виняток не приховуємо