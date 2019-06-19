from flask import jsonify, request, make_response, url_for, g, abort, current_app, send_from_directory
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import User
from app.api.auth import token_auth
from werkzeug.utils import secure_filename
import os
import warnings
import functools


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def deprecated(func): # todo: move somewhere out of this module
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func


def allowed_file(filename): # todo: move somewhere out of this module
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/users/<string:username>', methods=['GET'])
@token_auth.login_required
def get_user(username):
    return jsonify(User.query.filter_by(username=username).first_or_404().to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', username=user.username)
    return response


@deprecated
@bp.route('/users/<string:username>/deprecated', methods=['PUT'])
@token_auth.login_required
def update_user(username):
    if g.current_user.username != username:
        abort(403)
    user = User.query.filter_by(username=username).first_or_404()
    data = request.get_json() or {}
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('Please use different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/users/<string:username>', methods=['PUT'])
@token_auth.login_required
def update_user_multipart(username):
    if g.current_user.username != username:
        abort(403)
    user = User.query.filter_by(username=username).first_or_404()
    data = request.form.to_dict() or {}
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('Please use different email address')
    if 'picture' in request.files:
        picture = request.files["picture"]
        if picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            path = os.path.join(current_app.config['UPLOADS'], filename)
            picture.save(path)
            data['picture'] = url_for('api.send_file', filename=filename, _external=True)
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/images/<path:filename>')
def send_file(filename):  # todo: move this route out of API blueprint
    return send_from_directory(current_app.config['UPLOADS'], filename)


@bp.route('/users/upload', methods=['POST'])
def test_upload():
    name = request.form.get("name")
    image = request.files["image"]
    print(image)
    image.save(os.path.join(current_app.config['UPLOADS'], image.filename))
    print("Image saved")
    response = make_response(str(name) + " loh", 200)
    response.mimetype = "text/plain"
    return response
