from functools import wraps

from flask import render_template
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request

from learners.logger import logger
from learners.conf.config import cfg
from learners.conf.db_models import TokenBlocklist
from learners.database import db

jwt = JWTManager()


@jwt.expired_token_loader
def token_expired(jwt_header, jwt_payload):
    error_msg = "Your token is expired. Please login again."
    cfg.template["admin"] = False
    cfg.template["authenticated"] = False
    return render_template("login.html", **cfg.template, error=error_msg)


@jwt.invalid_token_loader
def token_invalid(jwt_payload):
    error_msg = "Your token is invalid."
    cfg.template["admin"] = False
    cfg.template["authenticated"] = False
    return render_template("login.html", **cfg.template, error=error_msg)


@jwt.token_verification_loader
def token_valid(jwt_header, jwt_data):
    cfg.template["authenticated"] = True
    return jwt_data


@jwt.unauthorized_loader
def token_missing(callback):
    error_msg = "Authorization is missing."
    cfg.template["admin"] = False
    cfg.template["authenticated"] = False
    return render_template("login.html", **cfg.template, error=error_msg)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    try:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None
    except Exception as e:
        logger.exception(e)
        return True


@jwt.revoked_token_loader
def token_revoked(jwt_header, jwt_payload):
    error_msg = "Token has been revoked."
    return render_template("login.html", **cfg.template, error=error_msg)


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()

            if get_jwt().get("admin"):
                cfg.template["admin"] = True
                cfg.template["authenticated"] = True
                return fn(*args, **kwargs)
            else:
                error_msg = "Admins only!"
                cfg.template["admin"] = False
                cfg.template["authenticated"] = False
                return render_template("login.html", **cfg.template, error=error_msg)

        return decorator

    return wrapper


def init_jwt(app):
    global jwt
    jwt.init_app(app)
