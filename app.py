# Flask / Flask modules
from flask import Flask, json
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import request
from flask.helpers import make_response

# SCSS Support
from flask_assets import Environment
from flask_jwt_extended.utils import decode_token, get_jwt, get_jwt_header
# Custom bundles
from util.assets import get_bundle

# JWT
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_bcrypt import Bcrypt

#  CORS
from flask_cors import CORS
from flask_cors import cross_origin

# DB
from flask_sqlalchemy import SQLAlchemy

# Apache Htpasswd
from passlib.apache import HtpasswdFile

# Misc
import requests
import os
from datetime import datetime
from datetime import timedelta
import time
import uuid

# ---------------------------------------------------------------------------------------

app = Flask(__name__)

# ---------------------------------------------------------------------------------------

# Temporarly set ENV variables
os.environ['CHARM_HTPASSWD'] = 'temp_htpasswd'

# HTPASSWD
htpasswd = os.getenv('CHARM_HTPASSWD', default="/etc/nginx/htpasswd")
ht = HtpasswdFile(htpasswd)

# JWT
jwt_secret = os.getenv('CHARM_JWT_SECRET', default="53CR3T")
app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=120)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# CONFIG
app.config['THEME'] = 'dark'
app.config['BRANDING'] = True

# CORS
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_ORIGINS'] = ['http://127.0.0.1:8888', 'http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:8888']
app.config['CORS_SUPPORTS_CREDENTIALS '] = True
cors = CORS(app)

# URLS
app.config['VENJIX_URL'] = "http://127.0.0.1:5001"
app.config['VNC_URL'] = "https://10.17.4.219/placeholder_1"
app.config['DOCS_URL'] = "http://localhost:8080" + "/en"
app.config['EXERCISES_URL'] = "http://localhost:8888" + "/en"
app.config['CALLBACK_URL'] = "http://127.0.0.1:5000/callback"

# DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learners_tracker.db"
db = SQLAlchemy(app)

# ---------------------------------------------------------------------------------------

# Assets
assets = Environment(app)
theme_bundle = get_bundle(app.config['THEME'])
assets.register(theme_bundle)

# ---------------------------------------------------------------------------------------

template_config = dict(
    branding = app.config['BRANDING'],
    theme = app.config['THEME'],
    docs_url = app.config['DOCS_URL'], 
    vnc_url = app.config['VNC_URL']
)

# ---------------------------------------------------------------------------------------

# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    posts = db.relationship('Post', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}')"

# History of sent POSTs
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.String(120), nullable=False)
    call_uuid = db.Column(db.String(120), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_time = db.Column(db.DateTime, nullable=True) 
    response_content = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"\nPost('id: {self.id}', \n'script_name: {self.script_name}', \n'call_uuid: {self.call_uuid}', \n'start_time: {self.start_time}', \n'response_time: {self.response_time}', \n'completed: {self.completed}', \n'user_id: {self.user_id}') \n -------------------------------------"
    
    def as_dict(self):
        return "{ 'start_time' : {self.start_time}, 'completed' : {self.completed} }"

# Create Database
db.create_all() 


# ---------------------------------------------------------------------------------------

def datetime_from_utc_to_local(utc_datetime, date=True):
    if (utc_datetime is not None):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        if (date):
            timestamp = (utc_datetime + offset).strftime("%m/%d/%Y, %H:%M:%S")
        else:
            timestamp = (utc_datetime + offset).strftime("%H:%M:%S")
        return timestamp
    else:
        return None

# ---------------------------------------------------------------------------------------

@jwt.expired_token_loader
def token_expired(jwt_header, jwt_payload):
    error_msg = "Your token is expired. Please login again."
    return render_template('login.html', **template_config, error=error_msg)


@jwt.invalid_token_loader
def token_invalid(jwt_payload):
    error_msg = "Your token is invalid."
    return render_template('login.html', **template_config, error=error_msg)

@jwt.unauthorized_loader
def token_missing(callback):
    error_msg = "Authorization is missing."
    return render_template('login.html', **template_config, error=error_msg)

# ---------------------------------------------------------------------------------------


@app.route('/')
def get_home():
    try:
        verify_jwt_in_request()
        success_msg = "Logged in as %s" % get_jwt_identity()
        return render_template('login.html', **template_config, success=success_msg)
    except:
        return render_template('login.html', **template_config)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', **template_config)
    else:
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        if not ht.check_password(username, password):
            error_msg = "Invalid username or password"
            return render_template('login.html', **template_config, error=error_msg)
        
        # keep track of users if they are logged in
        if User.query.filter_by(username = username).first() == None:
            authorized_user = User(username=username) 
            db.session.add(authorized_user)
            db.session.commit()

        response = redirect('/access')
        access_token = create_access_token(identity=username)
        set_access_cookies(response, access_token)
        return response


@app.route('/access')
@jwt_required()
def render_access():
    
    # Get JWT Token and append it to the exercises URL via query string
    user_id = get_jwt_identity()
    headers = request.cookies.get('access_token_cookie')
    exercises_url = app.config['EXERCISES_URL'] + '?auth=' + str(headers)

    return render_template(
        'index.html',
        **template_config,
        exercises_url = exercises_url, 
        id = user_id
        )



# ---------------------------------------------------------------------------------------
# Run a script on the external server (Venjix)
# ---------------------------------------------------------------------------------------

@app.route('/execute_script/<script>', methods=['POST'])
@cross_origin()
@jwt_required()
def execute_script_on_remote(script):

    # get user id from JWT token
    verify_jwt_in_request(locations='headers')
    user_jwt_identity = get_jwt_identity()
    
    # generate a unique identifier 
    # <user_jwt_identity>_<64-charater-random>
    call_uuid = str(user_jwt_identity) + '_{0}'.format(uuid.uuid4().int & (1<<64)-1)
    
    # pack payload to json object    
    payload = json.dumps({
        "script" : script,
        "user_id" : user_jwt_identity,
        "callback" : app.config['CALLBACK_URL'] + '/' + str(call_uuid)
    })
    
    user_id = User.query.filter_by(username = user_jwt_identity).first().id

    new_entry = Post(
        script_name = script,
        call_uuid = call_uuid,
        user_id = user_id 
        )
    db.session.add(new_entry)
    db.session.commit()
    
    # send POST request
    response = requests.post(
        url = app.config['VENJIX_URL'] + "/{0}".format(script), 
        headers = {'Content-type': 'application/json'},
        data = payload
    )

    # get response
    init_state = response.json()
    executed = bool(init_state['response'] == "script started")
    
    return jsonify( uuid = call_uuid, executed = executed )


# ---------------------------------------------------------------------------------------
# Callback 
# ---------------------------------------------------------------------------------------

@app.route('/callback/<call_uuid>', methods=['POST'])
def process_callback(call_uuid):

    feedback = request.get_json()

    db_entry = Post.query.filter_by(call_uuid = call_uuid).first()
    db_entry.response_time = datetime.utcnow()
    db_entry.response_content = json.dumps(feedback)
    db_entry.completed = int(feedback['returncode'] == 0)
    db.session.commit()

    return jsonify(completed = True)



# ---------------------------------------------------------------------------------------
# Get current state
# ---------------------------------------------------------------------------------------

@app.route('/current_state/<script>')
@cross_origin()
@jwt_required()
def get_state(script):

    # get user id from JWT token
    verify_jwt_in_request(locations='headers')
    user_jwt_identity = get_jwt_identity()

    db_entries = (db.session.query(Post)
                .filter_by(script_name = script)
                .join(User)
                .filter_by(username = user_jwt_identity)
                .order_by(Post.response_time.desc())
                .limit(10)
                .all()
                )

    history = {}
    i = 1
    for db_entry in db_entries:
        new_history_entry = {
            'start_time' : datetime_from_utc_to_local(db_entry.start_time, date = True),
            'response_time' : datetime_from_utc_to_local(db_entry.response_time, date = False),
            'completed' : db_entry.completed
        }
        indicator = "post_{0}".format(i)
        history[indicator] = new_history_entry
        i += 1

    if (db_entries):
        script_executed = bool(db_entries[0])
        completed = db_entries[0].completed

        return jsonify(
            script_executed = script_executed,
            completed = completed,
            history = history
            )
    else:
        return jsonify(
            exercises = None
            )


# ---------------------------------------------------------------------------------------
# Check if exercise completed 
# ---------------------------------------------------------------------------------------

@app.route('/check_completion/<call_uuid>')
@cross_origin()
@jwt_required()
def check_completion(call_uuid):

    # get user id from JWT token
    verify_jwt_in_request(locations='headers')

    while True:
        time.sleep(0.5)

        db_entry = (Post.query
                    .filter_by(call_uuid = call_uuid)
                    .first()
                    )
                    
        if (db_entry == None):
            return jsonify( completed = False )
        elif (db_entry.response_time != None):
            return jsonify( completed = db_entry.completed )
        
        # force new query on db in the next iteration
        db.session.close()


# ---------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
