# Реекспорт: завдяки цьому файлу ззовні можна писати "from taxi import Fleet",
# а не довгі "from taxi.collections_ import Fleet". Це і є "публічний фасад" пакета.

from .collections_ import Fleet, FleetPages
from .context import DispatchSession
from .entities import Ride
from .errors import DuplicateEntity, EntityNotFound, TaxiError
from .values import GeoPoint, GeoPointDC

# __all__ - список імен, які пакет офіційно "показує назовні".
# Впливає на "from taxi import *" (без __all__ зірочка тягнула б і приватні речі) і слугує документацією:
# з одного погляду видно всі публічні класи бібліотеки.
__all__ = ["GeoPoint", "GeoPointDC", "Ride", "Fleet", "FleetPages",
           "DispatchSession", "TaxiError", "EntityNotFound", "DuplicateEntity"]