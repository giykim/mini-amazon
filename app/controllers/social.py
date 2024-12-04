from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app import db
import json
import datetime

from app.models.product import Product
from app.models.user import User
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('social', __name__)


@bp.route('/product-review', methods=['GET'])
def product_review():
    # Retrieve product info for review
    product_id = request.args.get('product_id')

    product = Product.get(product_id)

    return render_template('product_review.html', product=product)


@bp.route('/new-product-review', methods=['POST'])
def new_product_review():
    # Recieve info from user to create a review for user specified product
    pid = request.form.get('product_id')
    rating = request.form.get('rating')
    description = request.form.get('description')

    if current_user.is_authenticated:
        # Only allow a given user to have one review per product
        already_exists = Review.new_product_review(current_user.id, pid, rating, description)

        if already_exists:
            flash("You've already reviewed this product.", "error")

    return redirect(url_for('products.product_page', product_id=pid))


@bp.route('/seller-review', methods=['GET'])
def seller_review():
    # Retrieve the info needed to display a seller review
    sid = request.args.get('seller_id')

    seller = User.get(sid)

    return render_template('seller_review.html', seller=seller)


@bp.route('/new-seller-review', methods=['POST'])
def new_seller_review():
    #Recieve info from user to create a review for user specified product
    sid = request.form.get('seller_id')
    rating = request.form.get('rating')
    description = request.form.get('description')

    if current_user.is_authenticated:
        # Only allow a given user to have one review per seller
        already_exists = Review.new_seller_review(current_user.id, sid, rating, description)

        if already_exists:
            flash("You've already reviewed this seller.", "error")

    return redirect(url_for('inventories.get_user', uid=sid))


@bp.route('/edit-review', methods=['POST'])
def edit_review():
    """
    Route to go to form to edit existing review
    """
    rid = request.form.get('review_id')

    review_info = Review.get_review_info(rid)[0]

    return render_template('edit_review.html', review_info=review_info)


@bp.route('/update-review', methods=['POST'])
def update_review():
    """
    Route to update existing review with new values
    """
    rid = request.form.get('review_id')
    rating = request.form.get('rating')
    description = request.form.get('description')

    Review.update_review(rid, rating, description)

    flash("You've updated your review!", "error")

    return redirect(url_for('users.review_history'))


@bp.route('/delete-review', methods=['POST'])
def delete_review():
    rid = request.form.get('review_id')

    Review.delete_review(rid)

    flash("Deleted review.", "error")

    return redirect(url_for('users.review_history'))
