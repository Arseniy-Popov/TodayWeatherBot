from datetime import date, timedelta

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from today_weather.config import CONFIG

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    default_locality_id = Column(Integer, ForeignKey("localities.id"))
    default_locality = relationship("Locality", foreign_keys=[default_locality_id])
    latest_locality_id = Column(Integer, ForeignKey("localities.id"))
    latest_locality = relationship("Locality", foreign_keys=[latest_locality_id])

    def __repr__(self):
        return f"<User: {self.id}>"


class AddressInput(Base):
    __tablename__ = "address_inputs"
    id = Column(Integer, primary_key=True)
    input = Column(String, unique=True, nullable=False)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=False)
    locality = relationship("Locality")
    date = Column(Date, default=date.today, nullable=False)

    def __repr__(self):
        return f"<AddressInput: from {self.input} to {self.locality.name}; {self.date}>"

    def is_expired(self):
        return date.today() - self.date > timedelta(
            days=int(CONFIG["CACHING"]["GEOCODING_PERIOD"])
        )


class Locality(Base):
    __tablename__ = "localities"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Locality: {self.name}>"
