from flask import Blueprint, send_from_directory, make_response, jsonify, request, Response
from backend.conf.config import cfg
import requests

from flask_jwt_extended import jwt_required

from backend.logger import logger

statics_api = Blueprint("statics_api", __name__)


@statics_api.after_app_request
def after_request_func(response):
    if jwt := request.args.get("jwt"):
        response.set_cookie("jwt_cookie", value=jwt, max_age=None, expires=None, path="/", domain=None, secure=None, httponly=False)
    return response


@statics_api.route("/statics", methods=["GET"])
@statics_api.route("/statics/", methods=["GET"])
@statics_api.route("/statics/<path:path>", methods=["GET"])
@jwt_required()
def getStaticFiles(path=""):
    # Load static defaults
    static_root = cfg.static_base_url  # Directory holding the static sites

    # Add "index.html" to path if empty or ends with "/"
    if not path or "." not in path:
        path = f"{path}index.html" if path.endswith("/") else f"{path}/index.html"

    try:
        return make_response(send_from_directory(static_root, path))

    except Exception:
        logger.exception(f"ERROR: Loading file failed: {path}")
        return jsonify(error="file not found"), 404


@statics_api.route("/proxy/<path:path>", methods=["GET", "POST"])
def proxy(path):
    if request.method == "GET":
        resp = requests.get(path)
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
            "content-security-policy",
            "content-security-policy-report-only",
        ]
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        headers.append(("Access-Control-Allow-Origin", "*"))
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == "POST":
        resp = requests.post(path, data=request.form)
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
            "content-security-policy",
            "server",
            "date",
        ]
        headers.append(("Access-Control-Allow-Origin", "*"))
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
