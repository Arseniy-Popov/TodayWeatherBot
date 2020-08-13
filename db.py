from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    default_address = Column(String)
    latest_address = Column(String)


engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def get_user(user_id):
    return session.query(User).filter(User.id == user_id).one_or_none()


def create_user(**kwargs):
    return User(**kwargs)


def get_user_attr(user_id, attr):
    user = get_user(user_id)
    if user is None:
        return None
    return getattr(user, attr)


def set_user_attr(user_id, attr, value):
    user = get_user(user_id)
    if user is None:
        user = create_user(**{id: user_id, attr: value})
        session.add(user)
        session.commit()
    else:
        setattr(user, attr, value)
