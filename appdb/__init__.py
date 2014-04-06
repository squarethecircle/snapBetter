from snapbetter import app
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)

from appdb import models

# db.drop_all()
db.create_all()

