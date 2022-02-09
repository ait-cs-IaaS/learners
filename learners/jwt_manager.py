from flask import render_template
from learners.config import cfg
from flask_jwt_extended import JWTManager


jwt = JWTManager()


@jwt.expired_token_loader
def token_expired(jwt_header, jwt_payload):
    error_msg = "Your token is expired. Please login again."
    return render_template("login.html", cfg.template, error=error_msg)


@jwt.invalid_token_loader
def token_invalid(jwt_payload):
    error_msg = "Your token is invalid."
    return render_template("login.html", cfg.template, error=error_msg)


@jwt.unauthorized_loader
def token_missing(callback):
    error_msg = "Authorization is missing."
    return render_template("login.html", cfg.template, error=error_msg)


def init_jwt(app):
    global jwt
    jwt.init_app(app)
