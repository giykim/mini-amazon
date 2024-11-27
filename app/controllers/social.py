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
    product_id = request.args.get('product_id')

    product = Product.get(product_id)

    return render_template('product_review.html', product=product)


@bp.route('/new-product-review', methods=['POST'])
def new_product_review():
    pid = request.form.get('product_id')
    rating = request.form.get('rating')
    description = request.form.get('description')

    if current_user.is_authenticated:
        already_exists = Review.new_product_review(current_user.id, pid, rating, description)

        if already_exists:
            flash("You've already reviewed this product.", "error")

    return redirect(url_for('products.product_page', product_id=pid))


@bp.route('/seller-review', methods=['GET'])
def seller_review():
    sid = request.args.get('seller_id')
    print(sid)

    seller = User.get(sid)

    print(seller)

    return render_template('seller_review.html', seller=seller)


@bp.route('/new-seller-review', methods=['POST'])
def new_seller_review():
    sid = request.form.get('seller_id')
    rating = request.form.get('rating')
    description = request.form.get('description')

    if current_user.is_authenticated:
        already_exists = Review.new_seller_review(current_user.id, sid, rating, description)

        if already_exists:
            flash("You've already reviewed this seller.", "error")

    return redirect(url_for('inventories.get_user', uid=sid))
