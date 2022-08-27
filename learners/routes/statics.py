from multiprocessing import shared_memory
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
    static_root = cfg.statics.get("directory")  # Directory holding the static sites
    shared_subfolders = cfg.statics.get("subfolders")  # e.g. "css", "js" (relevant for exercises and documentation)

    # Add "index.html" to path if empty or ends with "/"
    if (not path) or (not "." in path):
        path = f"{path}index.html" if path.endswith("/") else f"{path}/index.html"

    # Extract target base folder
    path_base = path.split("/")[0]

    try:
        # Attempt to load file from shared folder
        full_path = f"{path_base}/shared/{path}" if shared_subfolders in path.split("/") else path
        return send_from_directory(static_root, full_path)

    except:
        # If loading from shared folder fails

        serve_mode = "default"

        # Get serve mode: e.g. "user", "role"
        if path_base == "documentation":
            serve_mode = cfg.documentation.get("serve_mode")
        if path_base == "exercises":
            serve_mode = cfg.exercises.get("serve_mode")

        # Get username
        user_id = get_jwt_identity()
        path = path.split(f"{path_base}/")[1]

        if serve_mode == "user":
            full_path = f"{path_base}/{user_id}/{path}"
            print("1: ", full_path)

        elif serve_mode == "role":
            user_role = cfg.users.get(user_id).get("role")
            full_path = f"{path_base}/{user_role}/{path}"
            print("2: ", full_path)

        else:
            # Fallback to default
            full_path = f"{path_base}/{path}"
            print("3: ", full_path)

        try:
            return send_from_directory(static_root, full_path)
        except Exception as e:
            logger.exception(f"ERROR: Loading file failed: {path}")
            return make_response(jsonify(error="file not found"), 404)
