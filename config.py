import os

# SQLALCHEMY_DATABASE_URI = 'postgres://localhost:5432/snapbetter'

SQLALCHEMY_DATABASE_URI = 'postgres://secret_snapta:3stacksqSort@snapbetter.cdlasjxjiy0g.us-east-1.rds.amazonaws.com:5432/snapbetter'


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')



