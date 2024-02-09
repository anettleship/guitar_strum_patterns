from flask_login import LoginManager, UserMixin
from flask import redirect, url_for


class User(UserMixin):
    def __init__(self, id):
        self.id = id


class Auth:
    def __init__(self):
        self.login_manager = LoginManager()

    def init_app(self, app):
        self.login_manager.init_app(app)

        @self.login_manager.user_loader
        def load_user(user_id):
            return User(user_id)

        @self.login_manager.unauthorized_handler
        def handle_unauthorized():
            return redirect("/login", 401)

        return load_user
