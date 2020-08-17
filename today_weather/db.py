from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from today_weather.config import DATABASE_URI
from today_weather.models import Base, User

engine = create_engine(DATABASE_URI)
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
    else:
        setattr(user, attr, value)
    session.commit()
