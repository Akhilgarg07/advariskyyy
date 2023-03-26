from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from utils import Base


class Budget(Base):
    __tablename__ = 'budgets'
    budget_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=True, index=True)
    account_id = Column(Integer, ForeignKey(
        'accounts.account_id', ondelete='CASCADE'), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
