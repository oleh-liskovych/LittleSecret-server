from flask import Blueprint

bp = Blueprint('socket', __name__)

from app.socket import socket
