import os

from flask import Flask
from flask.logging import default_handler

from .log import log


def create_app():
    app = Flask(__name__,
                instance_path=os.path.abspath("./"),
                instance_relative_config=True,
                static_url_path='/static/',
                static_folder='../web/vue-admin-template/dist/static',
                template_folder='../web/vue-admin-template/dist')

    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    app.config.from_pyfile('config.py')

    app.logger.removeHandler(default_handler)
    app.logger = log

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import similar
    app.register_blueprint(similar.bp)
    from . import user
    app.register_blueprint(user.bp)

    from . import db
    app.teardown_appcontext(db.close_client)

    from . import tables
    data_path = app.config['DATA_PATH']
    with app.app_context():
        tables.init(data_path)

    return app
