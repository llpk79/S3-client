import os

from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from .database import db_session, init_db
from .forms import NewLoginForm
from .models import User, Role, Files, RoleUser

mail = Mail()
security = Security()
login_mngr = LoginManager()


def create_app() -> Flask.wsgi_app:
    """Create and configure a Flask WSGI application."""
    application = Flask(__name__.split(".")[0])
    print("App created.")

    # Load environment variables.
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    print("Environment variables loaded.")

    # Configure AWS access keys.
    application.config["SECRET_KEY"] = secret_key
    # app.config['SECURITY_CONFIRMABLE'] = True
    application.config["SECURITY_TRACKABLE"] = True
    application.config["SECURITY_PASSWORD_SALT"] = "salty"
    application.config["MAIL_SERVER"] = "smtp.gmail.com"
    application.config["MAIL_PORT"] = 587
    application.config["MAIL_USE_SSL"] = True
    application.config["MAIL_USERNAME"] = mail_username
    application.config["MAIL_PASSWORD"] = mail_password

    print("App configured.")

    # Add mail to app.
    mail.init_app(application.wsgi_app)

    # For user tracking.
    application.wsgi_app = ProxyFix(application.wsgi_app, 1)

    # Add login_manager.
    login_mngr.init_app(application.wsgi_app)
    login_mngr.login_view = "mylogin"

    from . import routes, auth

    application.register_blueprint(routes.bp)
    application.register_blueprint(auth.auth)

    # Setup Flask Security.
    user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
    security.init_app(application.wsgi_app, user_datastore, login_form=NewLoginForm)

    print("Security setup done.")

    # Connect database.
    print("Database connecting...")
    init_db()
    print("Database connected.")

    return application
