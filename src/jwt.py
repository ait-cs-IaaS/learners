from flask import Flask
from flask import render_template
from flask_jwt_extended import JWTManager

from src.app import app
from src.config import template_config

jwt = JWTManager(app)

@jwt.expired_token_loader
def token_expired(jwt_header, jwt_payload):
    error_msg = "Your token is expired. Please login again."
    return render_template('login.html', **template_config, error=error_msg)


@jwt.invalid_token_loader
def token_invalid(jwt_payload):
    error_msg = "Your token is invalid."
    return render_template('login.html', **template_config, error=error_msg)


@jwt.unauthorized_loader
def token_missing(callback):
    error_msg = "Authorization is missing."
    return render_template('login.html', **template_config, error=error_msg)
