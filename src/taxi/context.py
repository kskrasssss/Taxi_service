import copy
from types import TracebackType

from .collections_ import Fleet


class DispatchSession:
    """Атомарний пакет змін над Fleet: при винятку все відкочується."""

    def __init__(self, fleet: Fleet) -> None:
        self._fleet = fleet
        self._snapshot: Fleet | None = None   # знімок з'явиться лише в __enter__

    def __enter__(self) -> Fleet:
        # викликається на вході в блок "with DispatchSession(fleet) as s:"
        # deepcopy — ГЛИБОКА копія: копіюються й самі Ride всередині, а не лише список-обгортка
        self._snapshot = copy.deepcopy(self._fleet)
        return self._fleet   # у блоці with працюємо з тим самим fleet, не з копією

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: TracebackType | None) -> bool:
        # викликається при виході з блоку with, завжди — і при успіху, і при винятку
        if exc_type is not None and self._snapshot is not None:
            # відновлюємо стан НА МІСЦІ (через __dict__), а не self._fleet = self._snapshot —
            # інакше зовнішня змінна fleet лишилась би зі старим (зіпсованим) вмістом
            self._fleet.__dict__.update(self._snapshot.__dict__)
        self._snapshot = None
        return False   # НЕ ковтаємо виняток — він полетить далі до коду, що викликав with