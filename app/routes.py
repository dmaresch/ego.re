import os
from app import app,db
from flask import render_template,flash,redirect,url_for,send_from_directory,request
from forms import LoginForm,RegistrationForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
	#flash("test flash!")
	return render_template("index.html",title='Home')

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
	if(current_user.is_authenticated):
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data,email=form.email.data)
		user.set_password(form.password.data)
		user.set_role(1)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		flash('Congrats! You are now a registered user of ego.re')
		return redirect(url_for('profile'))
	return render_template('register.html',title='Register',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and user.check_password(password=form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(next_page or url_for('profile'))
		flash("Invalid username or password")
		return redirect(url_for('login'))
	return render_template('login.html',title='Sign In',form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
	return render_template("profile.html")

@app.route('/admin')
@login_required
def admin():
	if(not current_user.is_privileged()):
		return redirect(url_for('profile'))
	return render_template('admin.html',title='Admin',users=User.query.limit(50).all())

@app.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{'author': user, 'file_name':'test1.txt'},
		{'author': user, 'file_name':'test2.txt'}
	]
	return render_template('user.html',user=user,posts=posts)

@app.after_request
def set_response_headers(response):
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response

@app.route('/users')
def users():
	return render_template('users.html',users=User.query.limit(50).all())