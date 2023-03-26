import uuid
import json
import constants
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .auth import has_access
from utils.schemas import UserOut
from utils import get_db, get_cache, RedisCache, generate_report_task
from typing import Optional
import pandas as pd
from io import StringIO
from models import Expense, Budget, Account
import csv


router = APIRouter()

REDIS_KEY_PREFIX = constants.REDIS_KEY_PREFIX


@router.get("/{user_id}/reports/")
async def generate_report(user_id: int, current_user: UserOut = Depends(has_access), cache_client: RedisCache = Depends(get_cache), db: Session = Depends(get_db)):
    # get user's accounts

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    report_id = str(uuid.uuid4())
    REDIS_KEY = f"{REDIS_KEY_PREFIX}{report_id}"
    redis_value = json.dumps({"status": "started"})
    cache_client.set_(REDIS_KEY, redis_value, expiration_time=60 * 60 * 24)

    generate_report_task.delay(user_id, report_id)

    return {
        "report_id": report_id,
    }


@router.get("/{user_id}/reports/{report_id}")
async def get_report(user_id: int, report_id: str, current_user: UserOut = Depends(has_access), cache_client: RedisCache = Depends(get_cache)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    REDIS_KEY = f"{REDIS_KEY_PREFIX}{report_id}"
    report_data_redis = json.loads(cache_client.get(REDIS_KEY))

    report_status = report_data_redis.get("status", "error")
    report_data = report_data_redis.get("report_data", None)

    if report_status == 'started':
        return {
            "status": "running",
            "report_id": report_id,
        }
    else:
        return {
            "status": report_status,
            "report_id": report_id,
            "report_data": report_data,
        }
