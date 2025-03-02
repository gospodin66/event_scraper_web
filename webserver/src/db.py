from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlite3 import connect as sqlite_connect
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from os import path, mkdir, chmod
import stat
from contextlib import contextmanager

Base = declarative_base()

class Host(Base):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    events = relationship('Event', back_populates='host')

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'))
    event = Column(String, unique=True, nullable=False)
    link = Column(String, unique=True, nullable=False)
    when = Column(String, nullable=False)
    host = relationship('Host', back_populates='events')

class Database():
    DB = 'events.sqlite'
    DB_PATH = path.join(path.dirname(__file__), '..', 'events.db', DB)
    DATABASE_URL = f'sqlite:///{DB}'
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def __init__(self):
        if not Path(self.DB).exists():
            self.create_database()
            
        self.conn = sqlite_connect(self.DB)
        self.cursor = self.conn.cursor()
        self.session = self.SessionLocal()


    @contextmanager
    def get_db(self):
        try:
            yield self.session
        finally:
            self.session.close()

    def create_database(self):
        Base.metadata.create_all(bind=self.engine)
        chmod(self.DB, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)


    def create_table(self, model):
        model.__table__.create(bind=self.engine, checkfirst=True)


    def add_entity(self, entity):
        try:
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return entity
        except IntegrityError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()


    def get_entity(self, model, entity_id):
        try:
            return self.session.query(model).filter(model.id == entity_id).first()
        finally:
            self.session.close()


    def close(self):
        self.conn.close()


    def init_db(self) -> None:
        print("Initializing database")
        
        if not Path(self.DB_PATH).exists():
            print(f"Creating database directory: {path.dirname(self.DB_PATH)}")
            mkdir(path.dirname(self.DB_PATH))

        print("Creating database and tables")
        self.create_database()
        self.create_table(Event)
        self.create_table(Host)
        self.close()

        print("Database initialized.")


    def parse_and_save_result(self, result) -> int:

        if isinstance(result, dict) and result.get('status') == 'SUCCESS':
            events = result.get('events', [])
        else:
            return 0

        for event in events:
            venue_name = event.get('venue')
            event_name = event.get('name')
            link = event.get('link')
            when = event.get('when')

            print(f"Inserting record: Venue: {venue_name}, Event: {event_name}, Link: {link}, When: {when}")

            host = self.session.query(Host).filter_by(name=venue_name).first()
            if not host:
                host = Host(name=venue_name)
                try:
                    self.add_entity(host)
                except IntegrityError:
                    self.session.rollback()
                    host = self.session.query(Host).filter_by(name=venue_name).first()

            event = Event(event=event_name, link=link, when=when, host_id=host.id)
            try:
                self.add_entity(event)
            except IntegrityError:
                self.session.rollback()
                event = self.session.query(Event).filter_by(event=event_name, link=link).first()

        self.close()
        return 0
    

if __name__ == "__main__":
    db = Database()
    db.init_db()