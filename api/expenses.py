from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .auth import has_access
from utils import get_db
from models import Expense as ExpenseModel, Account as AccountModel
from utils.schemas import ExpenseCreate, ExpenseInDB, UserOut

router = APIRouter()


@router.post("/{user_id}/expenses/", response_model=ExpenseInDB)
def create_expense(
    user_id: int,
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(has_access)
):
    # Check if the logged in user is adding the expense for their own user ID
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    account = db.query(AccountModel).filter(
        AccountModel.account_id == expense.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account ID")

    total_expense = db.query(ExpenseModel).filter(
        ExpenseModel.account_id == expense.account_id).all()
    total_expense = sum([expense.amount for expense in total_expense])
    if total_expense + expense.amount > account.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Expense amount exceeds account balance")

    expense_data = expense.dict()
    expense_data['user_id'] = user_id
    db_expense = ExpenseModel(**expense_data)

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("/{user_id}/expenses/", response_model=List[ExpenseInDB])
def get_expenses(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    current_user: UserOut = Depends(has_access),
    db: Session = Depends(get_db)
):
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    filter_args = [ExpenseModel.user_id == user_id]
    if start_date:
        filter_args.append(ExpenseModel.date >= start_date)
    if end_date:
        filter_args.append(ExpenseModel.date <= end_date)
    if account_id:
        filter_args.append(ExpenseModel.account_id == account_id)
    if category:
        filter_args.append(ExpenseModel.category == category)

    expenses = db.query(ExpenseModel).filter(*filter_args).all()
    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expenses not found")

    return expenses
