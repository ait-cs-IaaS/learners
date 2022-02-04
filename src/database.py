from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from src.app import app

# ---------------------------------------------------------------------------------------
db = SQLAlchemy(app)
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