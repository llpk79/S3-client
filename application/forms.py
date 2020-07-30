from flask_security import LoginForm, url_for_security
from werkzeug.security import check_password_hash, generate_password_hash
from flask_security.forms import (
    StringField,
    BooleanField,
    SubmitField,
    requires_confirmation,
    Markup,
    PasswordField,
    password_required,
    password_length,
    email_validator,
    email_required,
)
from flask_security.utils import get_message, config_value
from flask import current_app, request
from .models import User
from sqlalchemy.exc import StatementError
from time import sleep


class NewLoginForm(LoginForm):
    email = StringField("Email", validators=[email_required, email_validator])
    password = PasswordField(
        "Password", validators=[password_required, password_length]
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None
        if not self.next.data:
            self.next.data = request.args.get("next", "")
        self.remember.default = config_value("DEFAULT_REMEMBER_ME")
        if (
            current_app.extensions["security"].recoverable
            and not self.password.description
        ):
            html = Markup(
                u'<a href="{url}">{message}</a>'.format(
                    url=url_for_security("forgot_password"),
                    message=get_message("FORGOT_PASSWORD")[0],
                )
            )
            self.password.description = html

    def validate_on_submit(self):
        if not super(LoginForm, self).validate():
            return False
        while True:  # Database may need to initialize before returning result.
            try:
                self.user = User.query.filter_by(email=self.email.data).one()
                break
            except StatementError:
                sleep(5)

        if self.user is None:
            self.email.errors.append(get_message("USER_DOES_NOT_EXIST")[0])
            # Reduce timing variation between existing and non-existing users
            generate_password_hash(self.password.data)
            return False
        if not self.user.password:
            self.password.errors.append(get_message("PASSWORD_NOT_SET")[0])
            # Reduce timing variation between existing and non-existing users
            generate_password_hash(self.password.data)
            return False
        if not check_password_hash(self.user.password, self.password.data):
            self.password.errors.append(get_message("INVALID_PASSWORD")[0])
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message("CONFIRMATION_REQUIRED")[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message("DISABLED_ACCOUNT")[0])
            return False
        return True
