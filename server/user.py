import flask
from flask import current_app, send_from_directory

__all__ = [
    'bp'
]

bp = flask.Blueprint('user', __name__)


@bp.route('/user/login', methods=['GET', 'POST'])
def user_login():
    return {
        'code': 20000,
        'data': {
            "token": 'admin-token'
        }
    }


@bp.route('/user/info', methods=['GET', 'POST'])
def user_info():
    return {
        "code": 20000,
        "data": {
            "roles": ['admin'],
            "introduction": 'I am a super administrator',
            "avatar": 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            "name": 'Super Admin'
        },
    }


@bp.route('/user/logout', methods=['GET', 'POST'])
def user_logout():
    return {
        "code": 20000,
        "data": 'success'
    }


@bp.route('/favicon.ico')
def get_fav():
    t_d = current_app.template_folder
    f_n = 'favicon.ico'
    # 它在模板目录
    return send_from_directory(t_d, f_n, cache_timeout=100)
