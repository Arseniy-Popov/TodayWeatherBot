from today_weather.config import get_db_uri
from today_weather.models import AddressInput, Base, Locality, User


session = None
engine = None


def get_or_none(model, field, value):
    return session.query(model).filter(getattr(model, field) == value).one_or_none()


def get_all(model):
    return list(session.query(model))


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
