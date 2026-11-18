from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from .settings import DATABASE_URL
from .models import Base
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine, 'connect')
    def sqlite_setup(conn, _):
        conn.execute('PRAGMA foreign_keys=ON')
Session = sessionmaker(bind=engine, expire_on_commit=False)
def get_db():
    with Session() as db:
        yield db

def init_db():
    Base.metadata.create_all(engine)
