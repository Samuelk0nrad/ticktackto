from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from typing import override

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ._base import Base

if TYPE_CHECKING:
    from ._move import Move
    from ._user import User

class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Game(Base):
    __tablename__: str = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    player_x_id: Mapped[str] = mapped_column(
        ForeignKey(column="users.user_name"), nullable=False
    )
    player_o_id: Mapped[str | None] = mapped_column(ForeignKey(column="users.user_name"), nullable=True)

    current_player: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=GameStatus.WAITING.value)

    winner_id: Mapped[str | None] = mapped_column(ForeignKey(column="users.user_name"), nullable=True)

    created_from: Mapped[str] = mapped_column(ForeignKey(column="users.user_name"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    player_x: Mapped["User"] = relationship(foreign_keys=[player_x_id], back_populates="games_as_x")
    player_o: Mapped["User | None"] = relationship(foreign_keys=[player_o_id], back_populates="games_as_o")
    created_from_user: Mapped["User"] = relationship(foreign_keys=[created_from], back_populates="games_created")
    winner: Mapped["User | None"] = relationship(foreign_keys=[winner_id], back_populates="games_won")
    moves: Mapped[list["Move"]] = relationship(
        back_populates="game", cascade="all, delete-orphan", order_by="Move.created_at"
    )

    @override
    def __repr__(self) -> str:
        return (
            f"Game(id={self.id}, player_x='{self.player_x_id}', "
            f"player_o='{self.player_o_id}', status='{self.status}', "
            f"created_from_user='{self.created_from_user.user_name}')"
        )
