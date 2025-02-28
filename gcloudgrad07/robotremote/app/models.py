from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Definição da tabela users
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.Text)

    robots = db.relationship('Robot', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Definição da tabela robots
class Robot(db.Model):
    __tablename__ = 'robots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ip_address = db.Column(db.String, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    robot_id = db.Column(db.String(255), nullable=False)
    robot_password = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='robots')

    def __repr__(self):
        return f'<Robot {self.name}>'
