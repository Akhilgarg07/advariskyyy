import os
import logging
import json
from datetime import datetime
from utils import get_db, get_cache
from models import Account as AccountModel, Expense, Budget
from celery import shared_task
from utils.redis import RedisCache

REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "report:")
ACCOUNT_PREFIX = os.getenv("ACCOUNT_PREFIX", "account:")


logger = logging.getLogger(__name__)


@shared_task()
def create_account_task(account_dict: dict, user_id: int, cache: RedisCache = get_cache()):
    db = next(get_db())

    db_account = AccountModel(
        **account_dict, user_id=user_id)

    db.add(db_account)
    db.commit()

    logger.info(f"New account created successfully: {db_account}")

    db.refresh(db_account)

    logger.info(f"New account refreshed successfully: {db_account}")

    cache_key = f"{ACCOUNT_PREFIX}{user_id}"
    cache.delete_key(cache_key)

    logger.info(f"Cache key deleted successfully: {cache_key}")

    return db_account


@shared_task
def generate_report_task(user_id, report_id, cache_client: RedisCache = get_cache()):

    db = next(get_db())

    accounts = db.query(AccountModel).filter(
        AccountModel.user_id == user_id).all()
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()

    # calculate total balance per account
    account_balance = {}
    for account in accounts:
        account_balance[account.account_name] = account.balance

    # Calculate total expenses per account
    account_expenses = {}
    for account in accounts:
        account_expenses[account.account_name] = 0
        for expense in expenses:
            if expense.account_id == account.account_id:
                account_expenses[account.account_name] += expense.amount

    # Calculate total budget per account
    account_budgets = {}
    for account in accounts:
        account_budgets[account.account_name] = 0
        for budget in budgets:
            if budget.account_id == account.account_id:
                account_budgets[account.account_name] += budget.amount

    report_data = {
        'accounts': [
            {
                'name': account.account_name,
                'balance': account_balance[account.account_name],
                'expenses': account_expenses[account.account_name],
                'budgets': account_budgets[account.account_name]
            }
            for account in accounts
        ]
    }

    # Serialize report data to JSON

    redis_value = json.dumps({
        "status": "success",
        'report_data': report_data,
        'report_id': report_id,
    })

    # Save report data to cache
    cache_client.set_(f"{REDIS_KEY_PREFIX}{report_id}",
                      redis_value, expiration_time=60 * 60 * 24)

    # TODO: Figure out how to expose container IP to the outside world
    # # Write report to CSV file
    # datetime_now = datetime.now()
    # filename = f"{datetime_now}_report.csv"

    # with open(f"/app/reports/{filename}", mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['Account Name', 'Account balance',
    #                     'Total Expenses', 'Total Budget'])
    #     for account in accounts:
    #         writer.writerow([account.account_name, account_balance[account.account_name], account_expenses[account.account_name],
    #                         account_budgets[account.account_name]])

    # # Return report link
    # report_link = f"http://{os.environ.get('CONTAINER_IP', '')}:8000/reports/{filename}"
    # cache_client.set_(f"{REDIS_KEY_PREFIX}{report_id}",
    #                   report_link, expiration_time=60 * 60 * 24)

    return redis_value
