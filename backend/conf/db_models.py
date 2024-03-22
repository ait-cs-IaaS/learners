from backend.database import db
from sqlalchemy import func


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), unique=False, nullable=False, default="participant")
    admin = db.Column(db.Integer, nullable=False, default=0)
    meta = db.Column(db.String(), unique=False, nullable=True)
    submission = db.relationship("Submission", backref="user", lazy=True)
    usergroups = db.relationship("UsergroupAssociation", back_populates="user")


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(120), nullable=True)
    _type = db.Column(db.String(120), nullable=True)
    message = db.Column(db.String(240), nullable=True)
    recipients = db.Column(db.String(120), nullable=True)
    positions = db.Column(db.String(120), nullable=True)


class Usergroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship("UsergroupAssociation", back_populates="usergroup")


class UsergroupAssociation(db.Model):
    usergroup_id = db.Column(db.ForeignKey("usergroup.id"), primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    usergroup = db.relationship("Usergroup", back_populates="users")
    user = db.relationship("User", back_populates="usergroups")


parent_child_relationship = db.Table(
    "parent_child_relationship",
    db.Column("parent_id", db.Integer, db.ForeignKey("page.id"), primary_key=True),
    db.Column("child_id", db.Integer, db.ForeignKey("page.id"), primary_key=True),
)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(32), nullable=False)
    page_title = db.Column(db.String(120), nullable=True)
    language = db.Column(db.String(3), nullable=True)
    root_page_id = db.Column(db.String(32), nullable=True)
    params = db.Column(db.String(320), nullable=True)
    hierarchy = db.Column(db.Integer, nullable=True)
    hidden = db.Column(db.Integer, nullable=False, default=0)

    childs = db.relationship(
        "Page",
        secondary=parent_child_relationship,
        primaryjoin=(parent_child_relationship.c.parent_id == id),
        secondaryjoin=(parent_child_relationship.c.child_id == id),
        backref=db.backref("parent", lazy="dynamic"),
        lazy="dynamic",
    )


class Cache(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    exercise_id = db.Column(db.ForeignKey("exercise.id"), primary_key=True)
    form_data = db.Column(db.String(), nullable=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(), nullable=False)
    page = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Questionnaire(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    page_title = db.Column(db.String(120), nullable=False)
    parent_page_title = db.Column(db.String(120), nullable=False)
    root_weight = db.Column(db.Integer, nullable=False)
    parent_weight = db.Column(db.Integer, nullable=False)
    child_weight = db.Column(db.Integer, nullable=False)
    order_weight = db.Column(db.Integer, nullable=False)
    questions = db.relationship("QuestionnaireQuestion", backref="questionnaire", lazy=True)


class QuestionnaireQuestion(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    question = db.Column(db.String(), nullable=False)
    answer_options = db.Column(db.String(), nullable=False)
    language = db.Column(db.String(), nullable=False, primary_key=True)
    multiple = db.Column(db.Integer, nullable=False, default=1)
    active = db.Column(db.Integer, nullable=False, default=0)
    questionnaire_id = db.Column(db.String(), db.ForeignKey("questionnaire.id"), primary_key=True)


class QuestionnaireAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answers = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
    question_id = db.Column(db.Integer, db.ForeignKey("questionnaire_question.id"), nullable=False)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


class Exercise(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    local_exercise_id = db.Column(db.Integer, nullable=False)
    exercise_type = db.Column(db.String(120), nullable=False)
    exercise_name = db.Column(db.String(120), nullable=False)
    page_title = db.Column(db.String(120), nullable=False)
    parent_page_title = db.Column(db.String(120), nullable=False)
    root_weight = db.Column(db.Integer, nullable=False)
    parent_weight = db.Column(db.Integer, nullable=False)
    child_weight = db.Column(db.Integer, nullable=False)
    order_weight = db.Column(db.Integer, nullable=False)
    script_name = db.Column(db.String(120), nullable=True)
    submissions = db.relationship("Submission", backref="exercise", lazy=True)


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    filename_hash = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Submission(db.Model):
    # General Fields
    id = db.Column(db.Integer, primary_key=True)
    exercise_type = db.Column(db.String(120), nullable=False)
    execution_timestamp = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
    completed = db.Column(db.Integer, nullable=False, default=0)
    executed = db.Column(db.Integer, nullable=False, default=0)
    partial = db.Column(db.Integer, nullable=False, default=0)
    status_msg = db.Column(db.String(240), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_id = db.Column(db.String(32), db.ForeignKey("exercise.id"), nullable=False)

    # Form Submission
    form_data = db.Column(db.String(), nullable=True)

    # Script Submission
    execution_uuid = db.Column(db.String(120), unique=True, nullable=True)
    response_timestamp = db.Column(db.DateTime, nullable=True)
    response_content = db.Column(db.Text, nullable=True)
    script_response = db.Column(db.Text, nullable=True)


class Timetracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(120), nullable=True)
    pause_time = db.Column(db.String(120), nullable=True)
    offset = db.Column(db.Integer, nullable=False, default=0)
    running = db.Column(db.Integer, nullable=False, default=0)
