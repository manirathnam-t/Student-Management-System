import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads",
        "profile_pics"
    )

    # -------------------------
    # Cloudinary
    # -------------------------

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")

    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")

    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")