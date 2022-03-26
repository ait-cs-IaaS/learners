from flask import Blueprint, abort, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from learners.conf.config import cfg
from learners.logger import logger

statics_api = Blueprint("statics_api", __name__)


@statics_api.route("/documentation/", methods=["GET"])
@statics_api.route("/documentation", methods=["GET"])
@jwt_required()
def serve_documentation_index():
    try:
        path = f"{cfg.documentation.get('directory')}/{get_jwt_identity()}/"
        return send_from_directory(path, "index.html")
    except Exception as e:
        logger.exception(f"Loading documentation from {cfg.documentation.get('directory')} failed")
        abort(e)


@statics_api.route("/documentation/<path:path>", methods=["GET"])
@jwt_required()
def serve_documentation(path):
    try:
        path = f"{path}index.html" if path.endswith("/") else path
        full_path = f"{get_jwt_identity()}/{path}"
        return send_from_directory(cfg.documentation.get("directory"), full_path)
    except Exception as e:
        logger.exception(f"Loading documentation from {cfg.documentation.get('directory')} failed")
        abort(e)


@statics_api.route("/exercises/", methods=["GET"])
@statics_api.route("/exercises", methods=["GET"])
@jwt_required()
def serve_exercises_index():
    try:
        path = f"{cfg.exercises.get('directory')}/{get_jwt_identity()}/"
        return send_from_directory(path, "index.html")
    except Exception as e:
        logger.exception(f"Loading exercises from {cfg.exercises.get('directory')} failed")
        abort(e.code)


@statics_api.route("/exercises/<path:path>", methods=["GET"])
@jwt_required()
def serve_exercises(path):
    full_path = f"{path}index.html" if path.endswith("/") else path
    try:
        path = f"{path}index.html" if path.endswith("/") else path
        full_path = f"{get_jwt_identity()}/{path}"
        return send_from_directory(cfg.exercises.get("directory"), full_path)
    except Exception as e:
        logger.exception(f"Loading exercises from {cfg.exercises.get('directory')} failed")
        abort(e.code)
