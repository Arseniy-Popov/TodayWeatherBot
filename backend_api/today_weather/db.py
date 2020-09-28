from today_weather.models import AddressInput, Base, Locality


session = None
engine = None


def get_or_none(model, field, value):
    result = session.query(model).filter(getattr(model, field) == value).one_or_none()
    session.commit()
    return result


def write(obj):
    session.add(obj)
    session.commit()
    return obj