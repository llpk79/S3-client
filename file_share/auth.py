from flask import Blueprint, g, redirect, flash, render_template, request, url_for, session
from werkzeug.security import generate_password_hash
from file_share import db_session
from flask_login import login_manager
from .models import User
from urllib.parse import urlparse, urljoin
from flask_security import login_user, RegisterForm, logout_user
from .forms import NewLoginForm
from sqlalchemy.sql import select
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    print('logged in user ', user_id)

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).one()


login_manager.user_loader = load_logged_in_user


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth.route('/login', methods=['GET', 'POST'])
def mylogin():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = NewLoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User.query.filter_by(email=form.email.data).one()
        g.user = user
        session['user_id'] = user.id
        login_user(user, remember=form.remember.data)
        flash('Logged in successfully.')

        next_ = request.args.get('next')
        print('next ', next_)

        return redirect(next_) if next_ else redirect(url_for('routes.index'))
    else:
        print('no validation')
    return render_template('security/login_user.html', login_user_form=form)


@auth.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email_ = form.email.data
            password = form.password.data
            error = None

            stmt = select([User.id]).where(User.email == email_)
            result = db_session.execute(stmt).fetchone()

            print('result ', result, password)

            if result:
                error = 'User {} is already registered.'.format(email_)

            if error is None:
                user = User(email=email_, username=email_, password=generate_password_hash(password),
                            current_login_at=str(datetime.now()), active=True)
                db_session.add(user)
                db_session.commit()
                return redirect(url_for('auth.mylogin'))

            flash(error)
    return render_template('security/register_user.html', register_user_form=form)


@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('routes.index'))
