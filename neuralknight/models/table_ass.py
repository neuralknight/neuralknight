from .meta import Base
from sqlalchemy.exc import DBAPIError
from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Table,
)


table = Table(
    'association', Base.metadata,
    Column('game_link', Integer, ForeignKey('game.id')),
    Column('board_link', Integer, ForeignKey('board.id')))
