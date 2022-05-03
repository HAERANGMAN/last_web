from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.secret_key = 'super secret key'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ekdldksk@localhost:3306/testdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    db.init_app(app)
    migrate.init_app(app, db)

    import main

    app.register_blueprint(main.bp)


    return app
