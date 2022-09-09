from flask import Blueprint, abort, send_from_directory, make_response, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from learners.conf.config import cfg
from learners.logger import logger

statics_api = Blueprint("statics_api", __name__)


@statics_api.route("/statics", methods=["GET"])
@statics_api.route("/statics/", methods=["GET"])
@statics_api.route("/statics/<path:path>", methods=["GET"])
@jwt_required()
def serve_statics(path=""):

    # Load static defaults
    static_root = cfg.static_base_url  # Directory holding the static sites

    # Add "index.html" to path if empty or ends with "/"
    if not path or "." not in path:
        path = f"{path}index.html" if path.endswith("/") else f"{path}/index.html"

    try:
        return send_from_directory(static_root, path)
    except Exception as e:
        logger.exception(f"ERROR: Loading file failed: {path}")
        return make_response(jsonify(error="file not found"), 404)
