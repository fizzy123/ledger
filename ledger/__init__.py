import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from . import settings

app = Flask(__name__)
app.config.from_object(settings)
db = SQLAlchemy(app)
# SQLAlchemy complains if this isn't set
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
r_client = redis.StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])

# pylint: disable=wrong-import-position
# has to be at the end in order to avoid a dependancy loop
from . import views
from . import models
from . import functions
