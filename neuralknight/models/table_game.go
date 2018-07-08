from .meta import Base
from sqlalchemy.orm import relationship
from .table_ass import table
from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
)


class TableGame(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    game = Column(String, nullable=False, unique=True)
    player_one = Column(String, nullable=False, unique=True)
    player_two = Column(String, nullable=False, unique=True)
    one_won = Column(Boolean, nullable=False)
    two_won = Column(Boolean, nullable=False)
    board_link = relationship("TableBoard", secondary=table, back_populates="game_link")
