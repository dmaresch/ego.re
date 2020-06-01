import os
from app import app,db
from flask import render_template,flash,redirect,url_for,send_from_directory,request
from forms import LoginForm,RegistrationForm,UploadForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User,Role,File
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import hashlib

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
		user.set_role(Role.query.get(1))
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
			return redirect(next_page or url_for('user',username=user.username))
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

@app.route('/uploads/<foldername>/<filename>')
def uploaded_file(foldername,filename):
	print(str(app.config['UPLOAD_FOLDER'] + foldername))
	return send_from_directory(app.config['UPLOAD_FOLDER'] + foldername,filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload',methods=['GET','POST'])
@login_required
def upload_file():
	form=UploadForm()
	if form.validate_on_submit():
		if form.file.data is None or form.file.data.filename =='':
			flash('No selected file.')
			return redirect(url_for('upload'))
		file=request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filetype=filename.rsplit('.',1)[1].lower()
			directory=app.config['UPLOAD_FOLDER'] + hashlib.md5(current_user.username).hexdigest()
			if not os.path.exists(directory):
				os.mkdir(directory)

			file.save(os.path.join(directory,filename))
			filehash=None
			with open(os.path.join(directory,filename)) as f:
				filehash = hashlib.md5(f.read(400)).hexdigest()
				f.close()

			os.rename(os.path.join(directory,filename),os.path.join(directory,filehash+'.'+filetype))
			f=File(file_name=filename,file_hash=filehash,file_type=filetype,uploader=current_user.get_id())

			db.session.add(f)
			db.session.commit()
			current_user.set_hashed_name()
			db.session.add(current_user)
			db.session.commit()

			if(form.prof_pic.data is True):
				current_user.set_profile_image(f.id)
				db.session.add(current_user)
				db.session.commit()
			return redirect(url_for('user',username=current_user.username))
	return render_template('upload.html',title='Upload',form=form)

@app.route('/development')
def development():
	return render_template('development.html')