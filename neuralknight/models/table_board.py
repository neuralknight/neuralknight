from .meta import Base
from sqlalchemy.orm import relationship
from .table_ass import table
from sqlalchemy import (
    Column,
    String,
    Integer,
)


class TableBoard(Base):
    __tablename__ = 'board'
    id = Column(Integer, primary_key=True)
    board_state = Column(String, nullable=False)
    move_num = Column(Integer, nullable=False)
    player = Column(String, nullable=False)
    game = Column(String, nullable=False)
    game_link = relationship("TableGame", secondary=table, back_populates="board_link")
