from sqlalchemy import Engine
from sqlalchemy.orm import Session

from BACKEND_NAME_PLACEHOLDER.model import Entity, Person, User
from BACKEND_NAME_PLACEHOLDER.schema import EntityBase


class Crud:
    def __init__(self, engine: Engine):
        self._engine: Engine = engine

    def get_users(self, filter: str | None = None) -> list[User]:
        if not filter:
            return []
        return []

    def get_persons(self, filter: str | None = None) -> list[Person]:
        if not filter:
            return []
        return []

    def get_entities(self, filter: str | None = None) -> list[Entity]:
        if not filter:
            return []
        return []

    def create_entity(self, new_entity: EntityBase):
        with Session(self._engine) as session:
            assert new_entity
            assert session
