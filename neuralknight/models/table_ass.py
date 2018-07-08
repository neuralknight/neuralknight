from .meta import Base
from sqlalchemy import (
    Column,
    Integer,
    Table,
    ForeignKey,
)


table = Table(
    'association', Base.metadata,
    Column('game_link', Integer, ForeignKey('game.id')),
    Column('board_link', Integer, ForeignKey('board.id')))
