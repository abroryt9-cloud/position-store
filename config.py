import os

class Config:
    SECRET_KEY = 'position-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///position.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024