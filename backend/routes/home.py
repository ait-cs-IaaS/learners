from flask import Blueprint, redirect, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from backend.logger import logger

home_api = Blueprint("home_api", __name__)


@home_api.route("/", methods=["GET"])
def home():

    # response = {
    #     "headline": "Welcome to",
    #     "headlineHighlight": "Learners",
    #     "welcomeText": """This is the entry point to the virtual environment of the simulation.<br>
    #     Please log in with your assigned credentials:""",
    # }
    # return jsonify(response)

    try:
        verify_jwt_in_request()
        return redirect("/result/all") if get_jwt().get("admin") else redirect("/access")

    except Exception:
        logger.info("No valid token present.")
        return redirect("/login")
