from flask import redirect, render_template
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from learners.conf.config import cfg
from functools import wraps


jwt = JWTManager()


@jwt.expired_token_loader
def token_expired(jwt_header, jwt_payload):
    error_msg = "Your token is expired. Please login again."
    return render_template("login.html", **cfg.template, error=error_msg)


@jwt.invalid_token_loader
def token_invalid(jwt_payload):
    error_msg = "Your token is invalid."
    return render_template("login.html", **cfg.template, error=error_msg)


@jwt.unauthorized_loader
def token_missing(callback):
    error_msg = "Authorization is missing."
    return render_template("login.html", **cfg.template, error=error_msg)


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["admin"]:
                cfg.template["authenticated"] = True
                return fn(*args, **kwargs)
            else:
                error_msg = "Admin only!"
                cfg.template["authenticated"] = False
                return render_template("login.html", **cfg.template, error=error_msg)

        return decorator

    return wrapper


def init_jwt(app):
    global jwt
    jwt.init_app(app)
