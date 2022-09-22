from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_security import LoginManagerSecurity, SQLAlchemyUserDatastore, Security
# from flask_caching import Cache
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcd'
    api = Api(app)
    admin = Admin(
        app,
        'Example: Auth',
        base_template='base.html',
        template_mode='bootstrap4',
    )  # για υπαλλήλους

    config = {
        "DEBUG": True,          # some Flask specific configs
        "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    }
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # flask security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    from .views import views, myAdminView
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Card, dvdModel, Role

    admin.add_view(myAdminView(dvdModel, db.session))

    # define a context processor for merging flask-admin's template context into the
    # flask-security views.
    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
