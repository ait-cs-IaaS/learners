from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from learners.config import set_config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def main():
    app = Flask(__name__)

    with app.app_context():
      bcrypt = Bcrypt(app)
      cors = CORS(app)
      set_config(app)
      db.init_app(app)
      db.create_all()
      jwt.init_app(app)

    from learners import views
    app.register_blueprint(views.bp)


    return app

