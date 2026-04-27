from typing import override
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base import Base
from ._entity import Entity

if TYPE_CHECKING:
    from ._game import Game
    from ._move import Move


class User(Base):
    __tablename__: str = "users"

    user_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey(column=Entity.id), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=True)

    entity: Mapped[Entity] = relationship()

    games_as_x: Mapped[list["Game"]] = relationship(foreign_keys="Game.player_x_id", back_populates="player_x")
    games_as_o: Mapped[list["Game"]] = relationship(foreign_keys="Game.player_o_id", back_populates="player_o")
    games_created: Mapped[list["Game"]] = relationship(
        foreign_keys="Game.created_from", back_populates="created_from_user"
    )
    games_won: Mapped[list["Game"]] = relationship(foreign_keys="Game.winner_id", back_populates="winner")
    moves: Mapped[list["Move"]] = relationship(back_populates="player")

    @override
    def __repr__(self) -> str:
        return f"User(user_name='{self.user_name}', password_hash='{self.password_hash}', entity={repr(self.entity)})"
