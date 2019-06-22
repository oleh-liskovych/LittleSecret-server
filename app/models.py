import base64
import jwt
from datetime import datetime, timedelta
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import enum
from time import time
from flask import current_app, url_for
from flask_login import UserMixin


class PresenceStatus(enum.Enum):
    unknown = 0
    available = 1
    offline = 2
    do_not_disturb = 3
    craving_communication = 4


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class UserPOV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False, default="")
    note = db.Column(db.String(1024), nullable=False, default="")
    mute_until = db.Column(db.DateTime, default=(datetime.utcnow() + timedelta(weeks=52)))
    mark = db.Column(db.String, nullable=False, default="")
    frequency = db.Column(db.Integer, nullable=False, default=0) # minimum interval between push notifications. seconds
    pov_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    original_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        data = {
            'id': self.id.name,
            'name': self.name,
            'note': self.note,
            'mute_until': self.mute_until.isoformat() + "Z",
            'mark': self.mark,
            'frequency': self.frequency,
            'contact': self.original.to_dict()
        }
        return data


class DeliveryStatus(enum.Enum):
    sent = 1
    received = 2
    seen = 3


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    last_online = db.Column(db.DateTime, default=datetime.utcnow())
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    name = db.Column(db.String(64), index=True, nullable=False, default="")
    bio = db.Column(db.String(1024), nullable=False, default="")
    picture = db.Column(db.String(512))
    presence_status = db.Column(db.Enum(PresenceStatus), default=PresenceStatus.unknown)
    in_foreground = db.Column(db.Boolean, nullable=False, default=False)
    shutdown_on_screen_off = db.Column(db.Boolean, nullable=False, default=False)

    originals = db.relationship('UserPOV', foreign_keys='UserPOV.original_id', backref='original', lazy='dynamic')
    povs = db.relationship('UserPOV', foreign_keys='UserPOV.pov_id', backref='pov', lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')

    def __repr__(self):
        return '<User {}, email: {}, bio: {}>'.format(self.username, self.email, self.bio)

    def delete_picture(self):
        self.picture = None
        db.session.add(self)

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
            'name': self.name,
            'bio': self.bio,
            'picture': self.picture,
            'last_online': self.last_online.isoformat() + 'Z',
            'status': self.presence_status.name,
            'shutdown_on_screen_off': self.shutdown_on_screen_off
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'name', 'bio', 'picture']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader # not sure it's needed when writing API
def load_user(id):
    return User.query.get(int(id))


class AbandonedPicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(512))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<AbandonedPicture owner_id {}, path {}>'.format(self.owner, self.path)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024), nullable=False, default="")
    time = db.Column(db.DateTime, default=datetime.utcnow())
    edited = db.Column(db.Boolean, default=False)
    deleted_for_author = db.Column(db.Boolean, default=False)
    deleted_for_recipient = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    delivery_status = db.Column(db.Enum(DeliveryStatus), default=DeliveryStatus.sent)

    def __repr__(self):
        return '<Message {}>'.format(self.text)




















