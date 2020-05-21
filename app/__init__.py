from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__,
	static_url_path='',
	static_folder='../web/static',
	template_folder='../web/templates')
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app,x_proto=1,x_host=1)
login=LoginManager(app)
login.login_view='login'
db=SQLAlchemy(app)
migrate=Migrate(app,db)

boostrap = Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

from app import routes,models