import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, current_app
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel, lazy_gettext as _l
from flask_socketio import SocketIO
import os


db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
login = LoginManager()
socketio = SocketIO()


def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    login.init_app(app)
    socketio.init_app(app, async_mode=None)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.common import bp as common_bp
    app.register_blueprint(common_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/ls.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.info('LittleSecret')

    # socketio.run(app, debug=True)
    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models

if __name__ == '__main__':
    print("if __name__ == '__main__':")
    socketio.run(current_app, debug=True)

