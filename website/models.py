from . import db
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField
from flask_admin.contrib.sqla import ModelView
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
import enum


class StatusOptions(enum.Enum):
    STILL_ACTIVE = 'Still Active'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'


class Card(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    data = db.Column(db.String(100))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.String(10), db.ForeignKey('dvd.id'))
    status = db.Column(db.Enum())


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    cards = db.relationship('Card')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


dvds = {}


class dvdModel(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))

    def get(self, id):
        result = dvdModel.query.get()
        return dvds[id]


class Order(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    card_id = db.Column(db.String, db.ForeignKey(Card.id))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    movie_id = db.Column(db.String(10), db.ForeignKey('dvdModel.id'))
   # status = db.Enum(db.String(10))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class myAdminView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
                )

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/'))

    can_create = True
    can_delete = True
    can_edit = True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class UserView(ModelView):
    can_delete = False
    can_edit = False


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# api.add_resource(dvd, "/dvd/<string:id>") add elsewhere
