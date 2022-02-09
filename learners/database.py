from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    posts = db.relationship("Post", backref="user", lazy=True)


# History of sent POSTs
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.String(120), nullable=False)
    call_uuid = db.Column(db.String(120), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_time = db.Column(db.DateTime, nullable=True)
    response_content = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


def build_db(app):
    global db
    db.init_app(app)
    db.create_all()
