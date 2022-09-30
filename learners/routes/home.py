from flask import Blueprint, redirect
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from learners.logger import logger

home_api = Blueprint("home_api", __name__)


@home_api.route("/", methods=["GET"])
def home():

    try:
        verify_jwt_in_request()
        return redirect("/result/all") if get_jwt().get("admin") else redirect("/access")

    except Exception:
        logger.info("No valid token present.")
        return redirect("/login")
