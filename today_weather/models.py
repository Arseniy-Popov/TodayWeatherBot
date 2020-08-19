from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


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
    input = Column(String)
    locality_id = Column(Integer, ForeignKey("localities.id"))
    locality = relationship("Locality")

    def __repr__(self):
        return f"<AddressInput: from {self.input} to {self.locality.name}>"


class Locality(Base):
    __tablename__ = "localities"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)

    def __repr__(self):
        return f"<Locality: {self.name}>"
