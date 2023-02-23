from flask import Blueprint, send_from_directory, make_response, jsonify, request
from flask_jwt_extended import current_user
from backend.conf.config import cfg
from backend.jwt_manager import jwt_required_any_location

from backend.logger import logger

statics_api = Blueprint("statics_api", __name__)


@statics_api.after_app_request
def after_request_func(response):
    if jwt := request.args.get("jwt"):
        response.set_cookie("jwt_cookie", jwt)
    return response


@statics_api.route("/statics", methods=["GET"])
@statics_api.route("/statics/", methods=["GET"])
@statics_api.route("/statics/<path:path>", methods=["GET"])
@jwt_required_any_location()
def serve_statics(path=""):

    # print("-----> Current user: {} {} {}".format(current_user.id, current_user.name, current_user.role))

    # Load static defaults
    static_root = cfg.static_base_url  # Directory holding the static sites

    # Add "index.html" to path if empty or ends with "/"
    if not path or "." not in path:
        path = f"{path}index.html" if path.endswith("/") else f"{path}/index.html"

    try:
        return make_response(send_from_directory(static_root, path))

    except Exception as e:
        logger.exception(f"ERROR: Loading file failed: {path}")
        return make_response(jsonify(error="file not found"), 404)
