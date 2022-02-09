from flask import Flask

from learners.config import build_config
from learners.database import build_db
from learners.jwt_manager import init_jwt


def main():

    app = Flask(__name__)

    with app.app_context():
        build_config(app)
        build_db(app)
        init_jwt(app)

    from learners import views

    app.register_blueprint(views.bp)

    return app
