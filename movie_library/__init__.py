import os

from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

from movie_library.routes import pages

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["MONGODB_URI"] = os.getenv("MONGODB_URI")
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "feQG5fKbEzinm1UB0ZuUK1mc1xdEEKclilK001YAKsA"
    )
    app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

    app.register_blueprint(pages)
    return app
