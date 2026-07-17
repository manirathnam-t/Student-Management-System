import os

from flask import Flask

from .extensions import db, login_manager, bcrypt

from .routes import main
from .auth import auth


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "your_secret_key"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Student Photo Upload Folder
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "students"
    )

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app