from functools import wraps
from flask import session, redirect, url_for, flash, request
from app.models.user import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this feature.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if "user_id" in session:
        from app.extensions import db
        return db.session.get(User, session["user_id"])
    return None
