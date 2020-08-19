from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from today_weather.config import DATABASE_URI
from today_weather.models import Base, User, AddressInput, Locality


engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def get_user(user_id):
    return session.query(User).filter(User.id == user_id).one_or_none()


def create_user(user_id, **kwargs):
    return User(id=user_id, **kwargs)


def get_user_attr(user_id, attr):
    user = get_user(user_id)
    if user is None:
        return None
    return getattr(user, attr)


def set_user_attr(user_id, attr, value):
    user = get_user(user_id)
    if user is None:
        user = create_user(user_id, **{attr: value})
        session.add(user)
    else:
        if isinstance(value, Base):
            session.add(value)
        setattr(user, attr, value)
    session.commit()


# def get_or_create(model, **kwargs):
#     if session.query(model).filter().one_or_none()
