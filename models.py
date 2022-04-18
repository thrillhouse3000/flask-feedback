from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

#MODELS go below
class User(db.Model):

    __tablename__ = 'users'

    @classmethod
    def register (cls, username, password, email, first_name, last_name, isAdmin=False):
        """hash users password"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name, isAdmin=isAdmin)
    
    @classmethod
    def authenticate (cls, username, password):
        """check for correct password"""
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    username = db.Column(
        db.String(20),
        primary_key=True,
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String,
        nullable=False
    )

    email = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    first_name = db.Column(
        db.String(30),
        nullable=False
    )

    last_name = db.Column(
        db.String(30),
        nullable=False
    )

    isAdmin = db.Column(
        db.Boolean,
        default=False
    )

    comment = db.relationship('Feedback', cascade='all, delete', backref='users')

class Feedback(db.Model):

    __tablename__ = 'comments'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.String(100),
        nullable=False,
    )

    content = db.Column(
        db.String,
        nullable=False
    )

    username = db.Column(
        db.String,
        db.ForeignKey('users.username')
    )

    user = db.relationship('User', backref='comments')