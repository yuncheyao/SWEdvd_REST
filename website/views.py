from tkinter import ACTIVE
from flask import Blueprint, render_template, request, flash, jsonify
from flask_security import login_required, current_user
from .models import Card, dvdModel, SearchForm, StatusOptions
from . import db
import json


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        card = request.form.get('card')
        new_card = Card(data=card, user_id=current_user.id,
                        StatusOptions=ACTIVE)
        db.session.add(new_card)
        db.session.commit()
        flash('Card added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-card', methods=['POST'])
def delete_card():
    card = json.loads(request.data)
    cardId = card['cardId']
    card = Card.query.get(cardId)
    if card:
        if card.user_id == current_user.id:
            db.session.delete(card)
            db.session.commit()

    return jsonify({})


@views.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    dvds = dvdModel.query
    if form.validate_on_submit():
        # Get data from submitted form
        dvds.searched = form.searched.data
        # Query the Database
        dvds = dvds.filter(dvdModel.name.like('%' + dvdModel.searched + '%'))
        dvds = dvds.order_by(dvdModel.id).all()

        return render_template("search.html",
                               form=form,
                               searched=dvds.searched,
                               dvds=dvds)
