import time
from datetime import datetime

from learners.database import User, Post, Form
from learners.conf.config import cfg
from learners.database import db


def utc_to_local(utc_datetime, date=True):
    if utc_datetime is None:
        return None
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return (utc_datetime + offset).strftime("%m/%d/%Y, %H:%M:%S") if date else (utc_datetime + offset).strftime("%H:%M:%S")


def get_history_from_DB(script_name, username):
    db_entries = (
        db.session.query(Post)
        .filter_by(script_name=script_name)
        .join(User)
        .filter_by(username=username)
        .order_by(Post.response_time.desc())
        .limit(10)
        .all()
    )

    history = {
        str(i + 1): {
            "start_time": utc_to_local(db_entry.start_time, date=True),
            "response_time": utc_to_local(db_entry.response_time, date=False),
            "completed": db_entry.completed,
        }
        for i, db_entry in enumerate(db_entries)
    }

    executed = bool(db_entries[0]) if db_entries else False
    completed = db_entries[0].completed if db_entries else False

    return executed, completed, history
