from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import sqlite3
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import re
import os
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
    when = Column(DateTime, nullable=False)
    host = relationship('Host', back_populates='events')

class Database():
    DB = 'events.sqlite'
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'events.db', DB)
    DATABASE_URL = f'sqlite:///{DB}'
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def __init__(self):
        if not Path(self.DB).exists():
            self.create_database()
        self.conn = sqlite3.connect(self.DB)
        self.cursor = self.conn.cursor()

    def create_database(self):
        Base.metadata.create_all(bind=self.engine)

    def create_table(self, model):
        model.__table__.create(bind=self.engine, checkfirst=True)

    def add_entity(self, entity):
        db = self.SessionLocal()
        try:
            db.add(entity)
            db.commit()
            db.refresh(entity)
            return entity
        finally:
            db.close()

    def get_entity(self, model, entity_id):
        db = self.SessionLocal()
        try:
            return db.query(model).filter(model.id == entity_id).first()
        finally:
            db.close()

    def close(self):
        self.conn.close()

def init_db() -> None:
    print("Initializing database")
    db = Database()
    if not Path(db.DB_PATH).exists():
        print(f"Creating database directory: {os.path.dirname(db.DB_PATH)}")
        os.mkdir(os.path.dirname(db.DB_PATH))
    print("Creating database and tables")
    db.create_database()
    db.create_table(Event)
    db.create_table(Host)
    db.close()
    print("Database initialized.")

def parse_and_save_result(result) -> int:
    db = Database()
    if isinstance(result, dict) and result.get('status') == 'SUCCESS':
        events = result.get('events', [])
    else:
        return 0

    for event in events:
        venue_name = event.get('venue')
        event_name = event.get('name')
        link = event.get('link')
        when_str = event.get('when')
        when = datetime.fromisoformat(when_str)

        print(f"Inserting record: Venue: {venue_name}, Event: {event_name}, Link: {link}, When: {when}")

        host = db.SessionLocal().query(Host).filter_by(name=venue_name).first()
        if not host:
            host = Host(name=venue_name)
            try:
                db.add_entity(host)
            except IntegrityError:
                db.SessionLocal().rollback()
                host = db.SessionLocal().query(Host).filter_by(name=venue_name).first()

        event = Event(event=event_name, link=link, when=when, host_id=host.id)
        try:
            db.add_entity(event)
        except IntegrityError:
            db.SessionLocal().rollback()
            event = db.SessionLocal().query(Event).filter_by(event=event_name, link=link).first()

    db.close()
    return 0

if __name__ == "__main__":
    init_db()