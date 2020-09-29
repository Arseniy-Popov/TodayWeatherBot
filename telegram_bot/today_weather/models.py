from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    default_locality_id = Column(Integer)
    default_locality_name = Column(String)
    latest_locality_id = Column(Integer)
    latest_locality_name = Column(String)

    def __repr__(self):
        return f"<User: {self.id}>"


class Locality:
    def __init__(self, id):
        self.id = id
