from functools import wraps

from flask import make_response, render_template
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request

from learners_backend.logger import logger
from learners_backend.conf.config import cfg
from learners_backend.conf.db_models import TokenBlocklist, User
from learners_backend.database import db

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


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    username = jwt_data["sub"]
    return User.query.filter_by(name=username).one_or_none()


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


def jwt_required_any_location():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):

            valid_token = False
            for token_location in ["query_string", "headers", "cookies"]:
                try:
                    verify_jwt_in_request(locations=[token_location])
                    valid_token = True
                except Exception as e:
                    pass

            if valid_token:
                return fn(*args, **kwargs)
            else:
                return make_response("No valid token found.", 401)

        return decorator

    return wrapper


def init_jwt(app):
    global jwt
    jwt.init_app(app)
