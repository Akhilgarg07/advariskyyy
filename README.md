# How I pushed commit as [Linus Torvalds](https://en.wikipedia.org/wiki/Linus_Torvalds)

`git -c user.name='Linus Torvalds' -c user.email='torvalds@linux-foundation.org' commit -m "docker moment 2"`

# AdvaRisk - A Personal Finance Management Tool


1. Track expenses across multiple accounts
2. Create budgets and progress
3. Generate reports to gain insights into your spending habits

## Getting Started

To get started with AdvaRisk, you'll need to install Docker and Docker Compose on your local machine. Once you have Docker and Docker Compose installed, you can clone the project repository and run the following command to start the application:


`docker-compose up`

This command will start the application and all its dependencies (PostgreSQL, Redis, RabbitMQ, and Celery). Once the application is running, you can access it at http://localhost:8000.

# Important Read below:

## There were few more things I could have done for this app but due to time constraints I was not able to, here are few

1. For DB operations having a seperate crud.py file
2. Generate a csv file for reports instead of json [:/](https://github.com/Akhilgarg07/advariskyyy/blob/277013a53c0ca26f6a2eaac5eaabff0f945fc18e/utils/tasks.py#L96)
