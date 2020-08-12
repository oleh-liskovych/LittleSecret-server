from app import create_app, db
from app.models import User
from flask_migrate import upgrade
import os
from config import HerokuConfig

app = create_app(HerokuConfig) # (os.getenv('FLASK_CONFIG') or 'default')


# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User}

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()


