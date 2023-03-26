import os

# redis stuff
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)
REDIS_KEY_PREFIX = os.getenv('REDIS_KEY_PREFIX', 'report:')

# celery
CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')

# SQL DB
SQLALCHEMY_DATABASE_URL = os.getenv(
    'SQLALCHEMY_DATABASE_URL', "sqlite:///./db.sqlite3")

# budget prefix redis key
BUDGET_PREFIX = os.getenv('BUDGET_PREFIX', 'budget:')

# account prefix redis key
ACCOUNT_PREFIX = os.getenv('ACCOUNT_PREFIX', 'account:')
