from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .controllers import index
    app.register_blueprint(index.bp)

    from .controllers import products
    app.register_blueprint(products.bp)

    from .controllers import users
    app.register_blueprint(users.bp)

    from .controllers import carts
    app.register_blueprint(carts.bp)

    return app
