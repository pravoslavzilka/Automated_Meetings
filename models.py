from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128))
    permit = Column(Integer)

    def __repr__(self):
        return self.name

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    key = Column(String(80), default=uuid.uuid4().hex)
    admin_user = Column(Integer, ForeignKey('users.username'),nullable=False)
    user = relationship('User', backref=backref('schedule', lazy=True))

    def __repr__(self):
        return self.name


class Lessons(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    link = Column(String(80))
    start = Column(String(80))
    end = Column(Time)
    table_id = Column(Integer, ForeignKey('schedule.id'),nullable=False)
    table = relationship('Schedule',backref=backref('lessons', lazy=True))

    def __repr__(self):
        return self.name
