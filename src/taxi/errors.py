class TaxiError(Exception):
    """Базовий виняток домену."""


class EntityNotFound(TaxiError):
    def __init__(self, entity_id: str) -> None:
        super().__init__(f"поїздку з id {entity_id!r} не знайдено")
        self.entity_id = entity_id


class DuplicateEntity(TaxiError):
    def __init__(self, entity_id: str) -> None:
        super().__init__(f"поїздка з id {entity_id!r} уже є в колекції")
        self.entity_id = entity_id