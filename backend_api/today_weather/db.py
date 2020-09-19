from today_weather.config import get_db_uri
from today_weather.models import AddressInput, Base, Locality, User
from today_weather.router import app


def get_or_none(model, field, value):
    return app.session.query(model).filter(getattr(model, field) == value).one_or_none()


def get_all(model):
    return list(app.session.query(model))


def create_object(model, **kwargs):
    obj = model(**kwargs)
    app.session.add(obj)
    app.session.commit()
    return obj


def write(obj):
    app.session.add(obj)
    app.session.commit()


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
    app.session.commit()
