from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from today_weather.config import DATABASE_URI
from today_weather.models import Base, User, AddressInput, Locality


engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def get_or_none(model, field, value):
    return session.query(model).filter(getattr(model, value) == value).one_or_none()


def create_object(model, **kwargs):
    obj = model(**kwargs)
    session.add(obj)
    session.commit()
    return obj


def write(obj):
    session.add(obj)
    session.commit()


def get_obj_attr(model, field, identifier, attr):
    obj = get_or_none(model, field, identifier)
    if obj is None:
        return None
    return getattr(obj, attr)


def set_obj_attr(model, field, identifier, attr, value):
    obj = get_or_none(model, field, identifier)
    if obj is None:
        obj = create_object(model, **{field: identifier, attr: value})
    else:
        setattr(obj, attr, value)
    session.commit()


# def get_or_create(model, **kwargs):
#     if session.query(model).filter().one_or_none()
