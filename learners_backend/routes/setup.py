from datetime import datetime, timezone

from flask import Blueprint, make_response, redirect, render_template, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from learners_backend.conf.config import cfg

from learners_backend.logger import logger

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/setup/login", methods=["GET"])
def getLoginInfo():

    return jsonify(
        headline="Welcome to the",
        headlineHighlight="CyberRange",
        welcomeText="This is the entry point to the virtual environment of the simulation.<br>Please log in with your assigned credentials:",
        landingpage=cfg.landingpage,
        logo=cfg.logo,
    )


@setup_api.route("/setup/tabs", methods=["GET"])
@jwt_required(optional=True)
def getSidebar():

    current_identity = get_jwt_identity()

    tabs = [
        {"id": "documentation", "type": "default", "url": "http://localhost:5000/statics/hugo/participant/en/documentation"},
        {"id": "exercises", "type": "default", "url": "http://localhost:5000/statics/hugo/participant/en/exercises"},
        {"id": "presentations", "type": "default", "url": "http://localhost:5000/statics/hugo/participant/en/presentations"},
    ]

    if current_identity:
        return jsonify(tabs=tabs)
    else:
        return jsonify(tabs=None)
