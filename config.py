import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "just-in-case-secret-phrase-is-absent"

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    LANGUAGES = ['en', 'uk', 'ru']

    UPLOADS = "/Users/OlehLiskovych/Documents/STUDY/LittleSecret/static/uploads"
    STATIC = "/Users/OlehLiskovych/Documents/STUDY/LittleSecret/static"

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['steve.loyd000@gmail.com', 'dannogo@gmail.com']
    # MAIL_USE_TLS = False # TLS - 587
    # MAIL_USE_SSL = True  # SSL - 465

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
