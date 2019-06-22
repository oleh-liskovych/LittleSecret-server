from flask import jsonify, request, url_for, g, abort, current_app
from app import db
from app.common.utils import allowed_file, unique_filename_from
from app.api import bp
from app.api.errors import bad_request
from app.models import User, AbandonedPicture
from app.api.auth import token_auth
import os


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
    data = request.form.to_dict() or {}

    error_data = validate_create_user_form(data)
    if bool(error_data):
        return bad_request(error_data)

    if 'picture' in request.files:
        picture = request.files["picture"]
        if picture and allowed_file(picture.filename):
            filename = unique_filename_from(picture.filename)
            path = os.path.join(current_app.config['UPLOADS'], filename)
            picture.save(path)
            data['picture'] = url_for('common.send_file', filename=filename, _external=True)
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', username=user.username)
    return response


def validate_create_user_form(data):
    """Returns dictionary of errors"""
    error_data = {}
    if 'username' not in data or not data['username'].strip():
        error_data['username'] = 'Username is required'
    if 'email' not in data or not data['email'].strip():
        error_data['email'] = 'Email is required'
    if 'password' not in data or not data['password']:
        error_data['password'] = 'Password is required'

    if 'username' not in error_data and User.query.filter_by(username=data['username'].strip()).first():
        error_data['username'] = 'Please use a different username'
    if 'email' not in error_data and User.query.filter_by(email=data['email'].strip()).first():
        error_data['email'] = 'Please use a different email address'

    return error_data


@bp.route('/users/<string:username>', methods=['PUT'])
@token_auth.login_required
def update_user(username):
    if g.current_user.username != username:
        abort(403)
    user = User.query.filter_by(username=username).first_or_404()
    data = request.form.to_dict() or {}

    error_data = validate_update_user_form(data, user)
    if bool(error_data):
        return bad_request(error_data)

    if 'picture' in request.files:
        picture = request.files["picture"]
        if picture and allowed_file(picture.filename):
            filename = unique_filename_from(picture.filename)
            path = os.path.join(current_app.config['UPLOADS'], filename)
            picture.save(path)
            data['picture'] = url_for('common.send_file', filename=filename, _external=True)
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/users/picture', methods=['DELETE'])
@token_auth.login_required
def delete_profile_picture():
    print("loh")
    if g.current_user.picture:
        abandoned_name = "abandoned_" + unique_filename_from(g.current_user.picture)
        print("abandoned_name {}".format(abandoned_name))
        from_path = os.path.join(current_app.config['UPLOADS'], os.path.basename(g.current_user.picture))
        to_path = os.path.join(current_app.config['UPLOADS'], abandoned_name)
        os.rename(from_path, to_path)

        abandoned = AbandonedPicture(path=abandoned_name, owner=g.current_user.id)
        g.current_user.delete_picture()
        db.session.add(abandoned)
        db.session.commit()

    return '', 204


def validate_update_user_form(data, user):
    """Returns dictionary of errors"""
    error_data = {}
    if 'email' in data and \
            data['email'].strip() and \
            data['email'].strip() != user.email and \
            User.query.filter_by(email=data['email'].strip()).first():
        error_data['email'] = 'Please use a different email address'

    return error_data