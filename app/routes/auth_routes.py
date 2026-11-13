from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models.user import User, Notification
from app.models.career import CareerRole
from app.utils.auth import login_required, get_current_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("landing.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    roles = CareerRole.query.all()
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        target_career = request.form.get("target_career", "AI Engineer")
        study_hours = int(request.form.get("study_hours_per_week", 10))

        if not email or not password or not full_name:
            flash("All fields are required.", "danger")
            return render_template("register.html", roles=roles)

        if User.query.filter_by(email=email).first():
            flash("An account with this email address already exists. Please sign in.", "warning")
            return redirect(url_for("auth.login"))

        user = User(
            email=email,
            full_name=full_name,
            target_career=target_career,
            study_hours_per_week=study_hours
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Welcome notification
        notif = Notification(
            user_id=user.id,
            title="Welcome to SkillBridge AI! 🚀",
            message=f"Welcome {full_name}! Your target career is set to {target_career}. Begin by taking an assessment or analyzing your resume to uncover your skill gaps.",
            category="success"
        )
        db.session.add(notif)
        db.session.commit()

        session["user_id"] = user.id
        session["user_name"] = user.full_name
        flash(f"Account created successfully! Welcome to SkillBridge AI, {full_name}.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html", roles=roles)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.args.get("next") or request.form.get("next")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please verify your credentials.", "danger")
            return render_template("login.html")

        session["user_id"] = user.id
        session["user_name"] = user.full_name
        flash(f"Welcome back, {user.full_name}!", "success")
        return redirect(next_url or url_for("dashboard.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("auth.index"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    roles = CareerRole.query.all()

    if request.method == "POST":
        user.full_name = request.form.get("full_name", user.full_name).strip()
        user.target_career = request.form.get("target_career", user.target_career)
        user.study_hours_per_week = int(request.form.get("study_hours_per_week", user.study_hours_per_week))
        user.current_education = request.form.get("current_education", user.current_education)
        user.bio = request.form.get("bio", user.bio)

        new_password = request.form.get("new_password", "").strip()
        if new_password:
            user.set_password(new_password)
            flash("Password updated successfully.", "info")

        db.session.commit()
        session["user_name"] = user.full_name
        flash("Profile preferences updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("profile.html", user=user, roles=roles)
