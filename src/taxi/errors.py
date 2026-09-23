class TaxiError(Exception):
    """Базовий виняток домену — щоб зовнішній код міг ловити 'усі наші помилки' одним except."""


class EntityNotFound(TaxiError):
    def __init__(self, entity_id: str) -> None:
        super().__init__(f"поїздку з id {entity_id!r} не знайдено")
        self.entity_id = entity_id   # id зберігаємо окремим атрибутом — раптом знадобиться коду, що ловить виняток


class DuplicateEntity(TaxiError):
    def __init__(self, entity_id: str) -> None:
        super().__init__(f"поїздка з id {entity_id!r} уже є в колекції")
        self.entity_id = entity_id