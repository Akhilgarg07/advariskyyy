import os
import logging
from fastapi import FastAPI
from utils import db, get_cache
from api import users, auth, accounts, expenses, budgets, reports
from celery import Celery


app = FastAPI()

db.create_database()

# lazy load redis cache
get_cache()

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')

celery_app = Celery(__name__, broker=CELERY_BROKER_URL)
celery_app.autodiscover_tasks()

# differnet queue for each task
celery_app.conf.task_routes = {
    'utils.tasks.create_account_task': {'queue': 'short_queue'},
    'utils.tasks.generate_report_task': {'queue': 'long_queue'}
}

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level)


app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(accounts.router, prefix="/api/users", tags=["accounts"])
app.include_router(expenses.router, prefix="/api/users", tags=["expenses"])
app.include_router(budgets.router, prefix="/api/users", tags=["budgets"])
app.include_router(reports.router, prefix="/api/users", tags=["reports"])


@app.get("/health")
def health():
    return {"status": "ok"}
