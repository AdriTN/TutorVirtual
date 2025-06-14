from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import get_settings

_settings = get_settings()

def get_engine(db_url: str | None = None, pool_size: int | None = None):
    url  = str(db_url or _settings.database_url)
    size = pool_size or _settings.pool_size
    return create_engine(url, pool_size=size, echo=False, future=True)


def get_db():
    from contextlib import contextmanager

    engine = get_engine()
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    @contextmanager
    def _session():
        db = Session()
        try:
            yield db
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    return _session()
