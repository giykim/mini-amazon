import os

from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'static'))
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

    from .controllers import inventories
    app.register_blueprint(inventories.bp)

    from .controllers import social
    app.register_blueprint(social.bp)

    # Ensure responses aren't cached
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    return app
