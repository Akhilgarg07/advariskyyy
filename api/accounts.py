import os
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from utils.schemas import AccountCreate, Account, UserOut, AccountUpdate
from utils import get_db, get_cache, RedisCache, create_account_task
from .auth import has_access
from typing import List
from models import Account as AccountModel


Logger = logging.getLogger(__name__)

router = APIRouter()

ACCOUNT_PREFIX = os.getenv("ACCOUNT_PREFIX", "account:")


@router.post("/{user_id}/accounts/")
async def create_account(
    user_id: int,
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(has_access)
):

    # Check if the logged in user is adding the account for their own user ID
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Check if the account already exists
    db_account = db.query(AccountModel).filter(
        AccountModel.user_id == user_id,
        AccountModel.account_name == account.account_name
    ).first()

    if db_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists")

    account_data = account.dict()
    create_account_task.delay(account_data, user_id)

    return {
        "status": "success",
        "message": "Account creation started in the background",
    }


@router.get("/{user_id}/accounts", response_model=List[Account])
def get_accounts(
    user_id: int,
    current_user: UserOut = Depends(has_access),
    cache_client: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    """
    Get a list of all accounts for the current user.
    """

    cache_key = f"{ACCOUNT_PREFIX}{user_id}"
    cached_data = cache_client.get(cache_key)

    if cached_data:
        Logger.info("Returning cached data")
        return json.loads(cached_data)

    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    accounts = db.query(AccountModel).filter(
        AccountModel.user_id == user_id).order_by(AccountModel.account_id.desc()).all()

    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Accounts not found")

    accounts = jsonable_encoder(accounts)
    cache_client.set_(cache_key, json.dumps(accounts))

    return accounts


@router.get("/{user_id}/accounts/{account_id}", response_model=Account)
def get_account(
    user_id: int,
    account_id: int,
    current_user: UserOut = Depends(has_access),
    cache_client: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    """
    Get details of a single account for the current user.
    """

    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    cache_key = f"{ACCOUNT_PREFIX}{user_id}_{account_id}"
    cached_data = cache_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    account = db.query(AccountModel).filter(
        AccountModel.account_id == account_id, AccountModel.user_id == user_id).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account_ = jsonable_encoder(account)
    cache_client.set_(cache_key, json.dumps(account_))
    return account


@router.put("/{user_id}/accounts/{account_id}")
def update_account(
    user_id: int,
    account_id: int,
    account: AccountUpdate,
    current_user: UserOut = Depends(has_access),
    cache: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    """
    Update an existing account for the current user.
    """

    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_account = db.query(AccountModel).filter(
        AccountModel.account_id == account_id, AccountModel.user_id == user_id).first()

    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account_data = account.dict(exclude_unset=True)
    for key, value in account_data.items():
        setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)

    cache_key = f"{ACCOUNT_PREFIX}{user_id}_{account_id}"
    cache.delete_key(cache_key)

    cache_key_accounts = f"{ACCOUNT_PREFIX}{user_id}"
    cache.delete_key(cache_key_accounts)

    return db_account


@router.delete("/{user_id}/accounts/{account_id}")
def delete_account(
    user_id: int,
    account_id: int,
    current_user: UserOut = Depends(has_access),
    cache: RedisCache = Depends(get_cache),
    db: Session = Depends(get_db)
):
    """
    Delete an existing account for the current user.
    """

    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_account = db.query(AccountModel).filter(
        AccountModel.account_id == account_id, AccountModel.user_id == user_id).first()

    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    db.delete(db_account)
    db.commit()

    cache_key = f"{ACCOUNT_PREFIX}{user_id}_{account_id}"
    cache.delete_key(cache_key)

    cache_key_accounts = f"{ACCOUNT_PREFIX}{user_id}"
    cache.delete_key(cache_key_accounts)

    return {"message": "Account deleted successfully"}
