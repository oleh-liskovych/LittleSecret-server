from flask import Blueprint

bp = Blueprint('common', __name__, template_folder='templates')

from app.common import routes, utils
