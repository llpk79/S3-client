from application import db_session
from datetime import datetime
from flask import (
    Blueprint,
    g,
    redirect,
    flash,
    render_template,
    request,
    url_for,
    session,
)
from flask_login import login_manager
from flask_security import login_user, RegisterForm, logout_user
from sqlalchemy.exc import StatementError
from sqlalchemy.sql import select
from time import sleep
from werkzeug.security import generate_password_hash

from .forms import NewLoginForm
from .models import User

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.before_app_request
def load_logged_in_user():
    """Loads a user object from Aurora if session['user_id'] is set, else returns None."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        while True:  # Database may need to initialize before returning result.
            try:
                g.user = User.query.filter_by(id=user_id).one_or_none()
                break
            except StatementError as e:
                print(e)
                sleep(5)


login_manager.user_loader = load_logged_in_user


@auth.route("/login", methods=["GET", "POST"])
def mylogin():
    """Login view."""
    form = NewLoginForm()
    user = None
    if form.validate_on_submit():  # Password checked here.
        while True:  # Database may need to initialize before returning result.
            try:
                user = User.query.filter_by(email=form.email.data).one_or_none()
                break
            except StatementError as e:
                print(e)
                sleep(5)
        if user:
            g.user = user
            session["user_id"] = user.id
            login_user(user, remember=form.remember.data)

            next_ = request.args.get("next")

            return redirect(next_) if next_ else redirect(url_for("routes.index"))
    return render_template("security/login_user.html", login_user_form=form)


@auth.route("/register", methods=("GET", "POST"))
def register():
    """Register view."""
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        email_ = form.email.data
        password = form.password.data
        error, result = None, None

        # Check if user already exists in database. Flash an error message if so.
        stmt = select([User.id]).where(User.email == email_)
        while True:  # Database may need to initialize before returning result.
            try:
                result = db_session.execute(stmt).fetchone()
                break
            except StatementError:
                sleep(5)
        if result:
            error = f"User {email_} is already registered."

        # Add user to database. Redirect to login page.
        if error is None:
            user = User(
                email=email_,
                username=email_,
                password=generate_password_hash(password),
                current_login_at=f"{datetime.now()}",
                active=True,
            )
            db_session.begin()
            db_session.add(user)
            db_session.commit()
            return redirect(url_for("auth.mylogin"))

        flash(error)
    return render_template("security/register_user.html", register_user_form=form)


@auth.route("/logout")
def logout():
    """Logout view."""
    g.user = None
    session["user_id"] = None
    logout_user()
    return redirect(url_for("routes.index"))
