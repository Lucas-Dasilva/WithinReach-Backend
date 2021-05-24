from datetime import datetime

from sqlalchemy.sql.elements import False_
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

class User(db.Model):
    id = db.Column('id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    karma = db.Column(db.Integer, default = 100)
    def serialize(self):
        return {"id": self.id,
                "karma": self.karma}
    posts = db.relationship('Post', backref='writer', lazy='dynamic')
    reactions = db.relationship('reactedPost', backref='user', lazy='dynamic')
    reactionsR = db.relationship('reactedReply', backref='user', lazy='dynamic')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    likes = db.Column(db.Integer, default= 1)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    replies = db.relationship('Reply', backref='replypost', lazy='dynamic')
    reactions = db.relationship('reactedPost', backref='reactionpost', lazy='dynamic')

    def serialize(self):
        return {"id": self.id,
                "body": self.body,
                "likes": self.likes,
                "timestamp": self.timestamp,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "reply_count": self.replies.count(),
                "user_id": self.user_id}

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=1)
    post = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    reactions = db.relationship('reactedReply', backref='reactionreply', lazy='dynamic')

    def serialize(self):
        return {"id": self.id,
                "body": self.body,
                "timestamp": self.timestamp,
                "post": self.post,
                "likes": self.likes,
                "user_id": self.user_id}

#Post that user has reacted to
class reactedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.Integer, db.ForeignKey('post.id'))
    status = db.Column(db.Integer, default = 0)    # Nothing = 0, upvote = 1, downvote = -1
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    def serialize(self):
        return {"id": self.id,
                "post": self.post,
                "status": self.status,
                "user_id": self.user_id}

#Replys that user has reacted to
class reactedReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply = db.Column(db.Integer, db.ForeignKey('reply.id'))
    # Nothing = 0, upvote = 1, downvote = -1
    status = db.Column(db.Integer, default = 0)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    post = db.Column(db.Integer, db.ForeignKey('post.id'))

    def serialize(self):
        return {"id": self.id,
                "post": self.reply,
                "status": self.status,
                "user_id": self.user_id}




# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     username = db.Column(db.String(64), unique = True)
#     password_hash = db.Column(db.String(128))
#     latitude = db.Column(db.String(1500))
#     longitude = db.Column(db.String(1500))
#     karma = db.Column(db.Integer, default = 100)
#     def __repr__(self):
#         return '<User {}-{};>'.format(self.id, self.username)
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#     def get_password(self, password):
#         return check_password_hash(self.password_hash, password)
#     posts = db.relationship('Post', backref='writer', lazy='dynamic')
#     reactions = db.relationship('reactedPost', backref='user', lazy='dynamic')
#     reactionsR = db.relationship('reactedReply', backref='user', lazy='dynamic')




@login.user_loader
def load_user(id):
    return User.query.get(int(id))