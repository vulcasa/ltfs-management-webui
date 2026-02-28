from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-for-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tape_metadata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 导入路由
from app import routes
