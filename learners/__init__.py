from flask import Flask


def main():

    app = Flask(__name__)

    with app.app_context():
        from learners.conf.config import build_config

        build_config(app)
        from learners.database import build_db

        build_db(app)
        from learners.jwt_manager import init_jwt

        init_jwt(app)

        from flask_cors import CORS

        CORS(app)

    import learners.routes as routes

    app.register_blueprint(routes.home_api)
    app.register_blueprint(routes.authentication_api)
    app.register_blueprint(routes.interface_api)
    app.register_blueprint(routes.execution_api)
    app.register_blueprint(routes.comment_api)
    app.register_blueprint(routes.callback_api)
    app.register_blueprint(routes.statics_api)
    app.register_blueprint(routes.admin_api)

    return app


app = main()
