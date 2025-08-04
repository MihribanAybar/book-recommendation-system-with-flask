from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class FavoriteBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
