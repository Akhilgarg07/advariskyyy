from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from utils import Base


class Expense(Base):
    __tablename__ = 'expenses'
    expense_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=True)
    account_id = Column(Integer, ForeignKey(
        'accounts.account_id', ondelete='CASCADE'), nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=True, index=True)
    date = Column(Date, nullable=False, index=True)
    notes = Column(String(256), nullable=True)
