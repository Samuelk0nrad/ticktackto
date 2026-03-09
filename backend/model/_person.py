from typing import override

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ._entity import Entity


class Person(Entity):
    __tablename__: str = "persons"

    id: Mapped[int] = mapped_column(ForeignKey(column=Entity.id), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=255))

    @property
    def last_name(self) -> str:
        return self.name

    @last_name.setter
    def last_name(self, value: str) -> None:
        self.name = value  # pyright: ignore [reportUnannotatedClassAttribute]

    @override
    def __repr__(self):
        return f"Person(id={self.id}, last_name='{self.name}', first_name='{self.first_name}')"

    __mapper_args__: dict[str, str] = {
        "polymorphic_identity": "persons",
    }
