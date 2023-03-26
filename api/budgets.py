import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from .auth import has_access
from utils import get_db, get_cache, RedisCache
from models import Budget as BudgetModel, Expense as ExpenseModel
from utils.schemas import BudgetCreate, BudgetInDB, UserOut

router = APIRouter()

BUDGET_PREIFX = os.getenv("BUDGET_PREFIX", "budget:")


@router.post("/{user_id}/budgets/", response_model=BudgetInDB)
def create_budget(
    user_id: int,
    budget: BudgetCreate,
    current_user: UserOut = Depends(has_access),
    cache_client: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if budget.start_date > budget.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Start date should be less than end date")

    # Create the budget in the database
    db_budget = BudgetModel(**budget.dict(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)

    # Delete the budget from cache
    cache_key = f"{BUDGET_PREIFX}{user_id}"
    cache_client.delete_key(cache_key)

    return db_budget


@router.put("/{user_id}/budgets/{budget_id}", response_model=BudgetInDB)
def update_budget(
    user_id: int,
    budget_id: int,
    budget: BudgetCreate,
    current_user: UserOut = Depends(has_access),
    cache_client: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Update the budget in the database
    db_budget = db.query(BudgetModel).filter(
        BudgetModel.budget_id == budget_id, BudgetModel.user_id == user_id).first()

    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    # check if start date is less than end date
    if budget.start_date > budget.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Start date should be less than end date")

    for key, value in budget.dict(exclude_unset=True).items():
        setattr(db_budget, key, value)

    db.commit()
    db.refresh(db_budget)

    # Delete the budget from cache
    cache_key = f"{BUDGET_PREIFX}{user_id}"
    cache_client.delete_key(cache_key)

    return db_budget


@router.get("/{user_id}/budgets/", response_model=List[BudgetInDB])
def get_budgets(
    user_id: int,
    current_user: UserOut = Depends(has_access),
    cache_client: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    cache_key = f"{BUDGET_PREIFX}{user_id}"
    cached_data = cache_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    budgets = db.query(BudgetModel).filter(
        BudgetModel.user_id == user_id).all()

    if not budgets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budgets not found")

    budget_ = jsonable_encoder(budgets)
    cache_client.set_(cache_key, json.dumps(budget_))

    return budgets


@router.get("/{user_id}/accounts/{account_id}/budgets/{budget_id}/progress")
def get_budget_progress(
    user_id: int,
    account_id: int,
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(has_access)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    budget = db.query(BudgetModel).filter(
        BudgetModel.user_id == user_id,
        BudgetModel.account_id == account_id,
        BudgetModel.budget_id == budget_id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    expenses_sum = db.query(func.sum(ExpenseModel.amount)).filter(
        ExpenseModel.user_id == user_id,
        ExpenseModel.account_id == account_id,
        ExpenseModel.date >= budget.start_date,
        ExpenseModel.date <= budget.end_date,
    ).scalar() or 0.00

    progress_percent = round((expenses_sum / budget.amount) * 100, 2)

    return {
        "budget_id": budget.budget_id,
        "account_id": budget.account_id,
        "amount": budget.amount,
        "start_date": budget.start_date,
        "end_date": budget.end_date,
        "expenses_sum": expenses_sum,
        "progress_percent": progress_percent,
    }
