import enum
from sqlalchemy import Enum
from sqlalchemy.orm import registry, relationship
import sqlalchemy as db


mapper_registry = registry()
Base = mapper_registry.generate_base()

class CellStatus(enum.Enum):
    invalid = 1
    edited = 2      # Edited after being submitted, parsed, or computed
    submitted = 3   # Submitted but not yet parsed
    accepted = 4    # Successfully parsed, but not executed yet
    rejected = 5    # Failed to parse, no code was executed
    running = 6     # Successfully compiled and currently executing
    computed = 7    # Successfully compiled and executed (Gives no information on runtime errors)


class CodeCells(Base):
    __tablename__ = 'code_cells'
    msg_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(Enum(CellStatus))


class OutputCell(Base):
    __tablename__ = 'output_cells'
    # id = db.Column(db.Integer, primary_key=True)
    msg_id = db.Column(db.Integer, primary_key=True)
    is_temp = db.Column(db.BOOLEAN, default=False)


def init(engine):
    mapper_registry.metadata.create_all(engine)


