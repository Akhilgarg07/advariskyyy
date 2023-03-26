from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from utils import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    accounts = relationship('Account', backref='owner',
                            lazy=True, cascade="all, delete-orphan")
