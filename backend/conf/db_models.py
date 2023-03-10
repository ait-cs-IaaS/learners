# sourcery skip: avoid-builtin-shadow
from backend.database import db
from sqlalchemy import func


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), unique=False, nullable=False, default="participant")
    admin = db.Column(db.Integer, nullable=False, default=0)
    executions = db.relationship("Execution", backref="user", lazy=True)
    notifications = db.relationship("NotificationAssociation", back_populates="user")
    usergroups = db.relationship("UsergroupAssociation", back_populates="user")


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String(240), nullable=True)
    position = db.Column(db.String(120), nullable=True)
    users = db.relationship("NotificationAssociation", back_populates="notification")


class NotificationAssociation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sent = db.Column(db.Integer, nullable=False, default=0)
    notification_id = db.Column(db.ForeignKey("notification.id"))
    user_id = db.Column(db.ForeignKey("user.id"))
    notification = db.relationship("Notification", back_populates="users")
    user = db.relationship("User", back_populates="notifications")
    constraint = db.UniqueConstraint("notification_id", "user_id")


class Usergroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship("UsergroupAssociation", back_populates="usergroup")


class UsergroupAssociation(db.Model):
    usergroup_id = db.Column(db.ForeignKey("usergroup.id"), primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    usergroup = db.relationship("Usergroup", back_populates="users")
    user = db.relationship("User", back_populates="usergroups")


class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_type = db.Column(db.String(120), nullable=False)
    script = db.Column(db.String(120), nullable=True)
    execution_timestamp = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
    response_timestamp = db.Column(db.DateTime, nullable=True)
    response_content = db.Column(db.Text, nullable=True)
    form_data = db.Column(db.String(), nullable=True)
    msg = db.Column(db.String(240), nullable=True)
    execution_uuid = db.Column(db.String(120), unique=True, nullable=True)
    completed = db.Column(db.Integer, nullable=False, default=0)
    partial = db.Column(db.Integer, nullable=False, default=0)
    connection_failed = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    filename_hash = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    global_exercise_id = db.Column(db.String(120), nullable=False)
    local_exercise_id = db.Column(db.Integer, nullable=False)
    exercise_type = db.Column(db.String(120), nullable=False)
    exercise_name = db.Column(db.String(120), nullable=False)
    page_title = db.Column(db.String(120), nullable=False)
    parent_page_title = db.Column(db.String(120), nullable=False)
    root_weight = db.Column(db.Integer, nullable=False)
    parent_weight = db.Column(db.Integer, nullable=False)
    child_weight = db.Column(db.Integer, nullable=False)
    order_weight = db.Column(db.Integer, nullable=False)
    executions = db.relationship("Execution", backref="exercise", lazy=True)
    comments = db.relationship("Comment", backref="exercise", lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    global_exercise_id = db.Column(db.String(), db.ForeignKey("exercise.global_exercise_id"), nullable=False)


class Questionaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    global_questionaire_id = db.Column(db.String(120), nullable=False)
    local_questionaire_id = db.Column(db.Integer, nullable=False)
    questionaire_name = db.Column(db.String(120), nullable=False)
    page_title = db.Column(db.String(120), nullable=False)
    parent_page_title = db.Column(db.String(120), nullable=False)
    root_weight = db.Column(db.Integer, nullable=False)
    parent_weight = db.Column(db.Integer, nullable=False)
    child_weight = db.Column(db.Integer, nullable=False)
    order_weight = db.Column(db.Integer, nullable=False)


class QuestionaireQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    global_question_id = db.Column(db.String(120), nullable=False)
    local_question_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(), nullable=False)
    options = db.Column(db.String(), nullable=False)
    global_questionaire_id = db.Column(db.String(), db.ForeignKey("questionaire.global_questionaire_id"), nullable=False)


class QuestionaireAnswer(db.Model):
    class Meta:
        include_relationships = True
        load_instance = True

    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    global_question_id = db.Column(db.Integer, db.ForeignKey("questionaire_question.global_question_id"), nullable=False)
    global_questionaire_id = db.Column(db.String(), db.ForeignKey("questionaire.global_questionaire_id"), nullable=False)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)