from typing import override

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base import Base
from ._entity import Entity


class User(Base):
    __tablename__: str = "users"

    user_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey(column=Entity.id), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=True)

    entity: Mapped[Entity] = relationship()

    @override
    def __repr__(self) -> str:
        return f"User(user_name='{self.user_name}', password_hash='{self.password_hash}', entity={repr(self.entity)})"
