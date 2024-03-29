import logging
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


if not app.debug:

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_hendler = RotatingFileHandler('logs/mainblog.log', maxBytes=10240, backupCount=5)
    file_hendler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s: %(lineno)d]'))
    file_hendler.setLevel(logging.INFO)
    app.logger.addHandler(file_hendler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("My BLOG start UP!")


from apps import routes, models, errors

