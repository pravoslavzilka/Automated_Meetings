from sqlalchemy import Column, Integer, String, Time, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


association_table = Table('association', Base.metadata,
    Column('left_id', Integer, ForeignKey('users.id')),
    Column('right_id', Integer, ForeignKey('schedule.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128))
    permit = Column(Integer)
    active_table_id = Column(Integer, ForeignKey('schedule.id'))

    active_table = relationship("Schedule", foreign_keys=[active_table_id], back_populates="active_users")
    tables = relationship(
        "Schedule",
        secondary=association_table,
        back_populates="users")

    def __repr__(self):
        return self.username

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

    lessons = relationship("Lessons", back_populates="table")
    user = relationship('User', foreign_keys=[admin_user], backref=backref('schedule', lazy=True))
    active_users = relationship("User", back_populates="active_table",foreign_keys="[User.active_table_id]")
    users = relationship(
        "User",
        secondary=association_table,
        back_populates="tables")

    def __repr__(self):
        return self.name


class Lessons(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    link = Column(String(80))
    start = Column(Time)
    end = Column(Time)
    day = Column(String(10))
    col = Column(String(15))
    number = Column(Integer)
    table_id = Column(Integer, ForeignKey('schedule.id'))
    table = relationship('Schedule', back_populates="lessons")

    def __repr__(self):
        return self.name
