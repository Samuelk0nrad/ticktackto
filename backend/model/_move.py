from datetime import datetime
from typing import TYPE_CHECKING
from typing import override

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ._base import Base

if TYPE_CHECKING:
    from ._game import Game
    from ._user import User


class Move(Base):
    __tablename__: str = "moves"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    game_id: Mapped[int] = mapped_column(ForeignKey(column="games.id", ondelete="CASCADE"), nullable=False)
    player_id: Mapped[str] = mapped_column(ForeignKey(column="users.user_name"), nullable=False)
    positionx: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 - 3
    positiony: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 - 3

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    game: Mapped["Game"] = relationship(back_populates="moves")
    player: Mapped["User"] = relationship(back_populates="moves")

    @override
    def __repr__(self) -> str:
        return (
            f"Move(id={self.id}, game_id={self.game_id}, "
            f"player='{self.player_id}', positionx={self.positionx}, "
            f"positiony={self.positiony})"
        )
