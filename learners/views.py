from flask import json
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import request
from flask import Blueprint

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request

from flask_cors import cross_origin

import requests
from datetime import datetime, timedelta
import time
import uuid

from learners import db
from learners.helpers import datetime_from_utc_to_local
from learners.config import template_config, htpasswd
from learners.database import User, Post

bp = Blueprint("views", __name__)


@bp.route('/')
def home():

    """
    This function verifies if a valid jwt-token is present. Depending on this, 
    the user is either shown a success message or redirected to the plain login form. 
    """

    try:
        verify_jwt_in_request()
        success_msg = "Logged in as %s" % get_jwt_identity()
        return render_template('login.html', **template_config, success = success_msg)
    except:
        return render_template('login.html', **template_config)


@bp.route("/login", methods=['GET', 'POST'])
def login():

    """
    GET: The plain login form is displayed to the user.

    POST: Username and password are validated if they are present in the htpasswd file 
    and therefore authorized. If successful, a JWT token is created and the user is 
    redirected to the /access route.
    """

    if request.method == 'GET':
        return render_template('login.html', **template_config)

    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if not htpasswd.check_password(username, password):
        error_msg = "Invalid username or password"
        return render_template('login.html', **template_config, error = error_msg)

    """ 
    Keep track of users in the database. First it is checked if there is already a 
    corresponding entry for the logged in user in the database, if this is not 
    the case, it is created.
    """

    if User.query.filter_by(username = username).first() is None:
        authorized_user = User(username = username)
        db.session.add(authorized_user)
        db.session.commit()

    response = redirect('/access')
    access_token = create_access_token(identity = username)
    set_access_cookies(response, access_token)

    return response


@bp.route('/access')
@jwt_required()
def access():

    """
    This function is responsible for rendering the access page. For this the 
    'template_config' dict is filled with the necessary information which is 
    then rendered via the index.html template.
    
    template_config:
        user_id (string)        -> Username from JWT Token
        branding (boolean)      -> wheiter or not to display branding on the login page 
        theme (string)          -> 'dark' or 'light'
        vnc_clients (dict)      -> dict of vnc clients
        docs_url (string)       -> url of documentation page
        exercises_url (string)  -> url of exercise control page
    """

    # Get JWT Token and append it to the exercises URL via query string
    template_config['user_id'] = get_jwt_identity()
    jwt_token = request.cookies.get('access_token_cookie')

    try:

        """
        Since the exercises are defined specifically for each user, it is important that the 
        user can authenticate against them. The integration of the Exercises page is done via 
        an iFrame, therefore the token must be transmitted via the query string of the url and 
        is attached here.

        The exercises_url is composed of the base exercise url from the app-config, the port 
        assigned to the user, the language setting and the JWT token:

        'base_url:port/en?auth=jwt_token'
        """
        
        template_config['exercises_url'] = app.config['EXERCISES_URL'] + \
            ':' + app.config['PORT_LIST'][template_config.get('user_id')]['exercises'] + \
            '/' + app.config['LANGUAGE'] + \
            '?auth=' + str(jwt_token)
        
        """
        The documentation URL is not as strict and only needs to be appended to the corresponding port.

        'base_url:port'
        """

        template_config['docs_url'] = app.config['DOCS_URL'] + \
            ':' + app.config['PORT_LIST'][template_config.get('user_id')]['docs']

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
        
        for vnc_client, client_details in template_config['vnc_clients'].items():
            if app.config['JWT_FOR_VNC_ACCESS']:
                additional_claims = {
                    "target": str(client_details['target']),
                    "username": str(client_details['username']),
                    "password": str(client_details['password'])
                    }
                auth_url = 'https://' + client_details['server'] + \
                    '?auth=' + str(create_access_token(
                        identity = template_config.get('user_id'), 
                        additional_claims = additional_claims
                        ))
            else:
                auth_url = 'https://' + \
                    client_details['username'] + ':' + \
                    client_details['password'] + '@' + \
                    client_details['server']

            template_config['vnc_clients'][vnc_client].setdefault('url', auth_url)
        
    except:
        error_msg = "No exercises for this user."
        return render_template('login.html', **template_config, error=error_msg)

    return render_template(
        'index.html',
        **template_config
    )


# ---------------------------------------------------------------------------------------
# Run a script on the external server (Venjix)
# ---------------------------------------------------------------------------------------

@bp.route('/execute_script/<script>', methods=['POST'])
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
    verify_jwt_in_request(locations='headers')
    user_jwt_identity = get_jwt_identity()

    # generate uuid
    call_uuid = str(user_jwt_identity) + \
        '_{0}'.format(uuid.uuid4().int & (1 << 64)-1)

    # pack payload to json object
    payload = json.dumps({
        "script": script,
        "user_id": user_jwt_identity,
        "callback": app.config['CALLBACK_URL'] + '/' + str(call_uuid)
    })

    user_id = User.query.filter_by(username=user_jwt_identity).first().id

    new_entry = Post(
        script_name=script,
        call_uuid=call_uuid,
        user_id=user_id
    )
    db.session.add(new_entry)
    db.session.commit()

    # send POST request
    response = requests.post(
        url=app.config['VENJIX_URL'] + "/{0}".format(script),
        headers={
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + app.config['VENJIX_AUTH_SECRET']
        },
        data=payload
    )

    # get response
    init_state = response.json()
    executed = bool(init_state['response'] == "script started")

    return jsonify(uuid=call_uuid, executed=executed)


# ---------------------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------------------

@bp.route('/callback/<call_uuid>', methods=['POST'])
def callback(call_uuid):

    """
    This endpoint is passed to Venjix in order to respond to an execute script. If a response 
    is received, it is recorded in the database and 'completed' returned.
    """

    feedback = request.get_json()

    db_entry = Post.query.filter_by(call_uuid=call_uuid).first()
    db_entry.response_time = datetime.utcnow()
    db_entry.response_content = json.dumps(feedback)
    db_entry.completed = int(feedback['returncode'] == 0)
    db.session.commit()

    return jsonify(completed=True)


# ---------------------------------------------------------------------------------------
# Get current state
# ---------------------------------------------------------------------------------------

@bp.route('/current_state/<script>')
@cross_origin()
@jwt_required()
def get_state(script):

    """
    This function returns the last 10 results of the requested script, executed by the current 
    user (identified via JWT token Identity).
    """

    db_entries = (db.session.query(Post)
                  .filter_by(script_name = script)
                  .join(User)
                  .filter_by(username = get_jwt_identity())
                  .order_by(Post.response_time.desc())
                  .limit(10)
                  .all()
                  )

    history = {}
    for i, db_entry in enumerate(db_entries):
        history[str(i + 1)] = {
            'start_time': datetime_from_utc_to_local(db_entry.start_time, date=True),
            'response_time': datetime_from_utc_to_local(db_entry.response_time, date=False),
            'completed': db_entry.completed
        }

    if (db_entries):
        return jsonify(
            script_executed = bool(db_entries[0]),
            completed = db_entries[0].completed,
            history = history
        )
    else:
        return jsonify(
            exercises = None
        )


# ---------------------------------------------------------------------------------------
# Check if exercise completed
# ---------------------------------------------------------------------------------------

@bp.route('/check_completion/<call_uuid>')
@cross_origin()
@jwt_required()
def check_completion(call_uuid):

    """
    This function executes a repeated query of the database and monitors whether a response to a 
    given callback endpoint ('<call_uuid>') has already been received.
    """

    while True:
        time.sleep(0.5)

        db_entry = (Post.query
                    .filter_by(call_uuid = call_uuid)
                    .first()
                    )

        if (db_entry == None):
            return jsonify(completed=False)
        elif (db_entry.response_time != None):
            return jsonify(completed=db_entry.completed)

        # force new query on db in the next iteration
        db.session.close()

# ---------------------------------------------------------------------------------------
