from app import db,login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(32),index=True,unique=True)
	email=db.Column(db.String(120),index=True,unique=True)
	password_hash=db.Column(db.String(128))
	posts=db.relationship('Post',backref='author',lazy='dynamic')
	role=db.Column(db.Integer,db.ForeignKey('role.id'),default=1)

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash=generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def is_privileged(self):
		r= Role.query.get(self.role)
		return r.moderator or r.admin

	def set_role(self,role):
		self.role = role.id

	def get_id(self):
		return self.id

	def get_role(self):
		r=Role.query.get(self.role)
		return r.name

class Post(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
	file_hash=db.Column(db.String(64))
	file_type=db.Column(db.String(64))
	file_name=db.Column(db.String(64))

	def __repr__(self):
		return '<Post {}>'.format(self.file_name)

class Role(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(20))
	moderator=db.Column(db.Boolean(),default=False)
	admin=db.Column(db.Boolean(),default=False)

	def __repr__(self):
		return '<Role {}>'.format(self.name)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))