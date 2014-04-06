import os

SQLALCHEMY_DATABASE_URI = 'postgres://localhost:5432/snapbetter'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
