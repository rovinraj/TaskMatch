from flask import Flask
from app.config import Config
from app.db import init_pool, close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise database pool
    init_pool(app)
    app.teardown_appcontext(close_db)

    # Register routes
    from app.routes import bp
    app.register_blueprint(bp)

    return app
