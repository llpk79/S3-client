import os

from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from .database import db_session, init_db
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
    app.config['SECURITY_PASSWORD_SALT'] = True
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

    @app.before_first_request
    def create_user():
        """For first time setup of a test user."""
        # user_datastore.create_role(id='0', name='username', role='admin')
        # db_session.commit()
        # user_datastore.create_user(id=0, email='username', username='username',
        #                            password='password')
        # db_session.commit()
        pass

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # Register blueprints.
    with app.app_context():
        from . import routes, auth
        app.register_blueprint(routes.bp)
        app.register_blueprint(auth.auth)

        # Setup Flask Security.
        user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
        security.init_app(app, user_datastore)
        print('Security setup done.')

        # Connect database.
        print('Database connecting...')
        init_db()
        print('Database connected.')

    app.add_url_rule('/', endpoint='index')

    return app
