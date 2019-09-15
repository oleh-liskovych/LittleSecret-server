from flask import app
from flask import render_template

from app.common.utils import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[LittleSecret] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('reset_password.html',
                                         user=user, token=token))
