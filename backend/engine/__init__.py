from sqlalchemy import Engine, create_engine

from ..config import Config
from ..model import Base


def get_engine(config_file: str = "") -> Engine:
    config = Config.get_instance(config_file)
    engine = create_engine(config.connection_string)
    Base.metadata.create_all(engine)
    return engine
