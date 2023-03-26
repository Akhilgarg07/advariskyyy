from sqlalchemy import DateTime, Column, Integer, String, Float, ForeignKey
from sqlalchemy.sql import func
from utils.db import Base


class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=True)
    account_name = Column(String(50), nullable=False, index=True)
    balance = Column(Float, nullable=False, default=0.00)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f'Account: {self.account_name}'
