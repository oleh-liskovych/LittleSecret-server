from flask import current_app, send_from_directory, render_template
from app.common import bp


@bp.route('/favicon.ico')
def favicon():
    print("favicon")
    return send_from_directory(current_app.config['STATIC'], 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@bp.route('/images/<path:filename>')
def send_file(filename):
    return send_from_directory(current_app.config['UPLOADS'], filename)


@bp.route('/')
def index():
    return render_template('index.html', async_mode=None)
