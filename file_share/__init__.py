import os

from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from .database import db_session, init_db
from .forms import NewLoginForm
from .models import User, Role, Files, RoleUser, UserFiles

mail = Mail()
security = Security()
login_mngr = LoginManager()


def create_app():
    app = Flask(__name__)
    print('App created.')

    # Load environment variables.
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    print('Environment variables loaded.')

    # Configure AWS access keys.
    app.config['APP_DEBUG'] = True
    app.config['SECRET_KEY'] = secret_key
    # app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_TRACKABLE'] = True
    app.config['SECURITY_PASSWORD_SALT'] = "salty"
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = mail_password

    print('App configured.')

    # Add mail to app.
    mail.init_app(app)

    # For user tracking.
    app.wsgi_app = ProxyFix(app.wsgi_app, 1)

    # Add login_manager.
    login_mngr.init_app(app)
    login_mngr.login_view = 'mylogin'


    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db_session.remove()
    #
    # Register blueprints.
    # with app.app_context():
    from . import routes, auth
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.auth)

    # Setup Flask Security.
    user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
    security.init_app(app, user_datastore,
                      login_form=NewLoginForm)

    print('Security setup done.')

    # Connect database.
    print('Database connecting...')
    init_db()
    print('Database connected.')

    # app.add_url_rule('/', endpoint='index')

    return app
