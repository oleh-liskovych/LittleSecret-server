import base64
import jwt
from datetime import datetime
from hashlib import md5
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import enum
from time import time
from flask import current_app
from flask_login import UserMixin


class PresenceStatus(enum.Enum):
    unknown = 0
    available = 1
    offline = 2
    do_not_disturb = 3
    craving_communication = 4


class DeliveryStatus(enum.Enum):
    sent = 1
    received = 2
    read = 3


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_online = db.Column(db.DateTime, default=datetime.utcnow())
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    name = db.Column(db.String(64))
    status = db.Column(db.String(1024))
    picture = db.Column(db.String(256)) # todo: find out how to store pictures
    presence_status = db.Column(db.Enum(PresenceStatus))
    in_foreground = db.Column(db.Boolean)
    shutdown_on_screen_of = db.Column(db.Boolean)


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_online': self.last_online.isoformat() + 'Z',

        }
































