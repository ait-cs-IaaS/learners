from flask import Flask


def main():

    app = Flask(__name__)

    with app.app_context():
        from backend.conf.config import build_config

        build_config(app)
        from backend.database import build_db

        build_db(app)
        from backend.jwt_manager import init_jwt

        init_jwt(app)

        from flask_cors import CORS

        cors = CORS()
        cors.init_app(app)

    import backend.routes as routes

    app.register_blueprint(routes.authentication_api)
    app.register_blueprint(routes.notifications_api)
    app.register_blueprint(routes.stream_api)
    app.register_blueprint(routes.questionaires_api)
    app.register_blueprint(routes.executions_api)
    app.register_blueprint(routes.comments_api)
    app.register_blueprint(routes.cache_api)
    app.register_blueprint(routes.callback_api)
    app.register_blueprint(routes.statics_api)
    app.register_blueprint(routes.setup_api)
    app.register_blueprint(routes.exercises_api)
    app.register_blueprint(routes.users_api)

    return app


app = main()
