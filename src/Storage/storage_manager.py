
import sqlalchemy as db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import registry
from sqlalchemy.orm import sessionmaker

from Storage import cell_storage
from Storage.cell_storage import OutputCell, CodeCells, CellStatus

mapper_registry = registry()
Base = mapper_registry.generate_base()
session = None
_engine = None

class StorageManager:
    def __init__(self, file_path):
        global session, _engine
        _engine = db.create_engine(file_path)
        session_m = sessionmaker(bind=_engine)
        session = session_m()
        init()
        cell_storage.init(_engine)


class Messages(Base):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, primary_key=False, nullable=False)
    channel_id = db.Column(db.Integer, primary_key=False, nullable=False)
    guild_id = db.Column(db.Integer, primary_key=False, nullable=False)
    __table_args__ = (UniqueConstraint('message_id', 'channel_id', 'guild_id', name='_message_channel_guild_uc'),)


def init():
    global session, _engine
    mapper_registry.metadata.create_all(_engine)



def get_msg_by_id(msg_id):
    return session.query(Messages).filter(Messages.id == msg_id).one_or_none()



def get_associated_output_or_none(guild_id: int, channel_id: int, message_id: int):
    output_cell = session.query(OutputCell).join(Messages, Messages.id == OutputCell.msg_id) \
                                             .filter(Messages.guild_id == guild_id,
                                                     Messages.channel_id == channel_id,
                                                     Messages.message_id > message_id) \
                                             .order_by(Messages.message_id.asc()).first()
    return output_cell


def add_output_cell(guild_id: int, channel_id: int, message_id: int, temp=False):
    m = Messages(guild_id=guild_id, channel_id=channel_id, message_id=message_id)
    session.add(m)
    msg_id = session.query(Messages.id).filter(Messages.guild_id == guild_id,
                                               Messages.channel_id == channel_id,
                                               Messages.message_id == message_id).one_or_none()

    o = OutputCell(msg_id=msg_id[0], is_temp=temp)
    session.add(o)
    session.commit()


def get_all_code_cells():
    cells = session.query(Messages).join(CodeCells, CodeCells.msg_id == Messages.id).all()
    return cells

def get_all_code_cells_with_status(status: CellStatus):
    cells = session.query(Messages)\
        .join(CodeCells, CodeCells.msg_id == Messages.id)\
        .filter(CodeCells.status == status).all()
    return cells

def get_code_cell(guild_id: int, channel_id: int, message_id: int):

    cell = session.query(CodeCells).join(Messages, Messages.id == CodeCells.msg_id)\
                    .filter(Messages.guild_id==guild_id,
                            Messages.message_id == message_id,
                            Messages.channel_id==channel_id).one_or_none()
    return cell

def set_msg_status(guild_id: int, channel_id: int, message_id: int, status: CellStatus):

    cell = session.query(CodeCells).join(Messages, Messages.id == CodeCells.msg_id)\
                    .filter(Messages.guild_id==guild_id,
                            Messages.message_id == message_id,
                            Messages.channel_id==channel_id).one_or_none()
    if cell is None:
        msg = Messages(guild_id=guild_id, channel_id=channel_id, message_id=message_id)
        session.add(msg)
        session.commit()
        cell = CodeCells(msg_id=msg.id, status=status)

    cell.status = status
    session.merge(cell)
    session.commit()
    return cell.msg_id

def is_code_cell_active(guild_id: int, channel_id: int, message_id: int):

    cell = session.query(CodeCells)\
        .join(Messages, Messages.id==CodeCells.msg_id)\
        .filter(Messages.guild_id==guild_id, Messages.message_id == message_id, Messages.channel_id==channel_id)\
        .one_or_none()

    if cell is not None:
        return True
    return False


def get_temp_output_cells():
    output_cells = session.query(Messages)\
                            .join(OutputCell, Messages.id == OutputCell.msg_id)\
                            .filter(OutputCell.is_temp == 1).all()
    return output_cells

def get_perm_output_cells():
    output_cells = session.query(Messages)\
                            .join(OutputCell, Messages.id == OutputCell.msg_id)\
                            .filter(OutputCell.is_temp == 0).all()
    return output_cells

def remove_code_cell(msg):
    remove_cell(msg, CodeCells)

def remove_output_cell(msg):
    remove_cell(msg, OutputCell)

def remove_cell(msg, cell_type):
    msg_id = msg.id

    cell = session.query(cell_type).filter(cell_type.msg_id == msg_id).one_or_none()
    if cell is None:
        print("Something went VERY wrong when trying to clean the database...")
        return

    session.delete(cell)
    session.delete(msg)
    session.commit()

def get_output_cell_or_none(msg):
    cell = session.query(Messages)\
            .join(OutputCell, Messages.id == OutputCell.msg_id)\
            .filter(Messages.guild_id==msg.guild.id, Messages.channel_id==msg.channel.id, Messages.message_id==msg.id)\
            .one_or_none()
    return cell