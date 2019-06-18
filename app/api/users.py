from flask import jsonify, request, url_for, g, abort
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import User
from app.api.auth import token_auth


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


@bp.route('/users/<string:username>', methods=['PUT'])
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
