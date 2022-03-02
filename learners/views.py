from flask import json
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import request
from flask import Blueprint
from flask import send_from_directory

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request

from flask_mail import Message

from flask_cors import cross_origin

import requests
import uuid
import time
from datetime import datetime

from learners.helpers import utc_to_local, get_history_from_DB
from learners.database import User, Post, Form
from learners.conf.config import cfg
from learners.database import db
from learners.mail_manager import mail

bp = Blueprint("views", __name__)


@bp.route("/")
def home():
    """
    This function verifies if a valid jwt-token is present. Depending on this,
    the user is either shown a success message or redirected to the plain login form.
    """

    try:
        verify_jwt_in_request()
        return redirect("/access")
    except:
        return render_template("login.html", **cfg.template)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: The plain login form is displayed to the user.

    POST: Username and password are validated if they are present in the htpasswd file
    and therefore authorized. If successful, a JWT token is created and the user is
    redirected to the /access route.
    """

    if request.method == "GET":
        return render_template("login.html", **cfg.template)

    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if not cfg.htpasswd.check_password(username, password):
        error_msg = "Invalid username or password"
        cfg.template["authenticated"] = False
        return render_template("login.html", **cfg.template, error=error_msg)

    """
    Keep track of users in the database. First it is checked if there is already a
    corresponding entry for the logged in user in the database, if this is not
    the case, it is created.
    """

    if User.query.filter_by(username=username).first() is None:
        authorized_user = User(username=username)
        db.session.add(authorized_user)
        db.session.commit()

    response = redirect("/access")
    access_token = create_access_token(identity=username)
    set_access_cookies(response, access_token)
    cfg.template["authenticated"] = True

    return response


@bp.route("/access")
@jwt_required()
def access():
    """
    This function is responsible for rendering the access page. For this the
    'cfg.template' dict is filled with the necessary information which is
    then rendered via the index.html template.

    cfg.template:
        user_id (string)        -> Username from JWT Token
        branding (boolean)      -> wheiter or not to display branding on the login page
        theme (string)          -> 'dark' or 'light'
        vnc_clients (dict)      -> dict of vnc clients
        docs_url (string)       -> url of documentation page
        exercises_url (string)  -> url of exercise control page
    """

    # Get JWT Token and append it to the exercises URL via query string
    user_id = get_jwt_identity()
    cfg.template["authenticated"] = True
    jwt_token = request.cookies.get("access_token_cookie")

    try:

        """
        JWT In query string to pass to iframe
        'base_url/user/en?auth=jwt_token'
        """

        cfg.template["exercises_url"] = (
            f"{cfg.url_exercises}:" + f"{cfg.user_assignments[user_id].get('ports').get('exercises')}/" + f"{cfg.language}?auth={jwt_token}"
        )

        cfg.template["docs_url"] = cfg.url_documentation

        """
        There are two types of user-host mapping between Learners and the noVNC server, defined by
        the app-config 'JWT_FOR_VNC_ACCESS':

        1. JWT token with target host: The target host is defined as an additional parameter in the
          JWT token. In this case a separate JWT token is created and apended for each host in which
          the target host is defined.

          Required config:

          vnc_clients:
            client:
              server (string)   -> IP of the noVNC server
              target (int)      -> target host to connect to
              username (string) -> Username of client
              password (string) -> Password of client

        2. 1:1 Mapping: In case there is only one Client used, no target must be specified, in this
          case a simple username + password config can be used. In order to not transmit username
          and password over the wire option 1 can be chosen with 'target=0'.

          Required config:

          vnc_clients:
            client:
              server (string)   -> IP of the noVNC server
              username (string) -> Username of client
              password (string) -> Password of client

        """

        cfg.template["vnc_clients"] = cfg.user_assignments[user_id]["vnc_clients"]
        for vnc_client, client_details in cfg.user_assignments[user_id]["vnc_clients"].items():
            if client_details["server"] == "default":
                client_details["server"] = cfg.url_novnc
            if cfg.jwt_for_vnc_access:
                additional_claims = {
                    "target": str(client_details["target"]),
                    "username": str(client_details["username"]),
                    "password": str(client_details["password"]),
                }
                vnc_auth_token = create_access_token(identity=user_id, additional_claims=additional_claims)
                auth_url = f"https://{client_details['server']}?auth={vnc_auth_token}"
            else:
                auth_url = (
                    f"https://{client_details['server']}?"
                    + f"username={client_details['username']}&password={client_details['password']}&"
                    + f"target={client_details['target']}"
                )

            print(auth_url)
            cfg.template["vnc_clients"][vnc_client].setdefault("url", auth_url)

    except:
        error_msg = "No exercises for this user."
        return render_template("login.html", **cfg.template, error=error_msg)

    return render_template("index.html", **cfg.template)


# ---------------------------------------------------------------------------------------
# Run a script on the external server (Venjix)
# ---------------------------------------------------------------------------------------


@bp.route("/execute/<script>", methods=["POST"])
@cross_origin()
@jwt_required()
def call_venjix(script):

    """
    This function allows to trigger an exercise-script on the external server 'Venjix'.
    The request contains the script name, the user ID and a unique callback URL which is composed of
    the user ID and a 64 character long random string (call_uuid).

    'call_uuid' = <user_jwt_identity>_<64-charater-random>

    This call_uuid is also stored in the database to be able to react to the callback later.
    """

    # get user id from JWT token
    verify_jwt_in_request(locations="headers")
    user_jwt_identity = get_jwt_identity()

    # generate uuid
    call_uuid = str(user_jwt_identity) + "_{0}".format(uuid.uuid4().int & (1 << 64) - 1)

    # pack payload to json object
    payload = json.dumps(
        {
            "script": script,
            "user_id": user_jwt_identity,
            "callback": f"{cfg.url_callback}/{str(call_uuid)}",
        }
    )

    user_id = User.query.filter_by(username=user_jwt_identity).first().id

    new_entry = Post(script_name=script, call_uuid=call_uuid, user_id=user_id)
    db.session.add(new_entry)
    db.session.commit()

    # send POST request
    response = requests.post(
        url=cfg.url_venjix + "/{0}".format(script),
        headers={
            "Content-type": "application/json",
            "Authorization": f"Bearer {cfg.venjix_auth_secret}",
        },
        data=payload,
    )

    # get response
    init_state = response.json()
    executed = bool(init_state["response"] == "script started")

    return jsonify(uuid=call_uuid, executed=executed)


# ---------------------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------------------


@bp.route("/callback/<call_uuid>", methods=["POST"])
def callback(call_uuid):

    """
    This endpoint is passed to Venjix in order to respond to an execute script. If a response
    is received, it is recorded in the database and 'completed' returned.
    """

    feedback = request.get_json()

    db_entry = Post.query.filter_by(call_uuid=call_uuid).first()
    db_entry.response_time = datetime.utcnow()
    db_entry.response_content = json.dumps(feedback)
    db_entry.completed = int(feedback.get("returncode") == 0)
    db_entry.msg = feedback.get("msg") or None
    db.session.commit()

    return jsonify(completed=True)


# ---------------------------------------------------------------------------------------
# Get current state
# ---------------------------------------------------------------------------------------


@bp.route("/history/<script>")
@cross_origin()
@jwt_required()
def get_history(script):

    """
    This function returns the last 10 results of the requested script, executed by the current
    user (identified via JWT token Identity).
    """

    executed, completed, history = get_history_from_DB(script, get_jwt_identity())

    if executed:
        return jsonify(
            executed=executed,
            completed=completed,
            history=history,
        )
    else:
        return jsonify(never_executed=True)


# ---------------------------------------------------------------------------------------
# Check if exercise completed
# ---------------------------------------------------------------------------------------


@bp.route("/monitor/<call_uuid>")
@cross_origin()
@jwt_required()
def monitor(call_uuid):

    """
    This function executes a repeated query of the database and monitors whether a response to a
    given callback endpoint ('<call_uuid>') has already been received.
    """

    while True:
        time.sleep(0.5)

        db_entry = Post.query.filter_by(call_uuid=call_uuid).first()

        if db_entry is None:
            return jsonify(completed=False)
        elif db_entry.response_time != None:
            _, _, history = get_history_from_DB(db_entry.script_name, get_jwt_identity())
            return jsonify(completed=db_entry.completed, msg=db_entry.msg, history=history)

        # force new query on db in the next iteration
        db.session.close()


# ---------------------------------------------------------------------------------------
# Get form data
# ---------------------------------------------------------------------------------------


@bp.route("/form/<form_name>", methods=["GET", "POST"])
@cross_origin()
@jwt_required()
def get_formdata(form_name):

    # Get user identification
    verify_jwt_in_request(locations="headers")
    user_jwt_identity = get_jwt_identity()
    user_id = User.query.filter_by(username=user_jwt_identity).first().id

    # Check whether the form was already submitted
    prio_submission = db.session.query(Form).filter_by(user_id=user_id).filter_by(form_name=form_name).first()

    if request.method == "GET":
        """
        This function checks if the requested form has already been received. Returns 'completed'
        if an entry is found.
        """

        if prio_submission is not None:
            return jsonify(executed=True, completed=True)
        else:
            return jsonify(never_executed=True)

    if request.method == "POST":
        """
        This function takes form data and stores it in the database and can additionally, if specified
        by the "Method" parameter in the header, send the results by mail to the exercise administrator.
        """

        if prio_submission is not None:
            return jsonify(completed=False, msg="Form was already submitted.")

        form_data = json.dumps(request.form.to_dict(), indent=4, sort_keys=False)

        # Create database entry
        new_form = Form(user_id=user_id, form_name=form_name, form_data=form_data, timestamp=datetime.utcnow())
        db.session.add(new_form)
        db.session.commit()

        # if specified, send form data via email
        if request.headers.get("Method") == "mail":
            subject = "Form Submission: {} - {}".format(user_jwt_identity, form_name)

            mailbody = "<h1>Results</h1>" + "<h2>Information:</h2>"
            mailbody += "<strong>User:</strong> {}</br>".format(user_jwt_identity)
            mailbody += "<strong>Form:</strong> {}</br>".format(form_name)
            mailbody += "<h2>Data:</h2>"

            data = ""
            for (key, value) in request.form.to_dict().items():
                if not value:
                    value = "<i>-- emtpy --</i>"
                data += "<strong>{}</strong>: {}</br>".format(key, value)

            mailbody += "<p>{}</p></br>".format(data)

            msg = Message(subject, sender=("Venjix", "lenhard.reuter@e-caterva.com"), recipients=["lenhard.reuter@ait.ac.at"])
            msg.html = mailbody
            mail.send(msg)

        return jsonify(executed=True)


@bp.route("/documentation/", methods=["GET"])
@bp.route("/documentation", methods=["GET"])
def serve_documentation_index():
    return send_from_directory("static/documentation", "index.html")


@bp.route("/documentation/<path:path>", methods=["GET"])
def serve_documentation(path):
    full_path = path if not path.endswith("/") else "{0}index.html".format(path)
    return send_from_directory("static/documentation", full_path)
