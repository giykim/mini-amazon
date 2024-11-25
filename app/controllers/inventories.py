from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user

from app.models.inventory import Inventory
from app.models.seller import Seller
from app.models.product import Product
from app.models.user import User
from app.models.reviews import Review


from flask import Blueprint
bp = Blueprint('inventories', __name__)


@bp.route('/user', methods = ['GET'])
def get_user():
    # Get user id to display public page of
    uid = request.args.get('uid')
    if uid is None:
        if current_user.is_authenticated:
            # If no user id is passed, then show current user's profile page
            uid = current_user.id
        else:
            # If user is not logged in, send to invalid page
            uid = -1
    
    # Check if user is a seller
    seller = Seller.get(uid)
    if seller is None:
        is_seller = False
    else:
        is_seller = True

    # Get info for all types of users
    user_info = User.get(uid) if is_seller else None
    
    # Review pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 3

    # Products sold pagination parameters
    product_page = request.args.get('product_page', 1, type=int)
    product_per_page = 9

    # Get stock if seller
    if is_seller:
        stock = Inventory.get_sold_by_details_paginated(uid, product_page, product_per_page)
    else:
        stock = None

    # Retrieve paginated reviews
    total_reviews = Review.count_seller_reviews(uid) if is_seller else 0
    total_pages = (total_reviews + per_page - 1) // per_page
    seller_reviews = Review.get_seller_reviews_paginated(uid, page, per_page) if is_seller else None

    # Retrieve paginated products
    total_products = Inventory.count_sold_products(uid) if is_seller else 0
    product_total_pages = (total_products + product_per_page - 1) // product_per_page
    
    # Check if user is looking at their own profile
    mine = (current_user.id == uid)

    return render_template('user.html', 
                           uid=uid, 
                           is_seller=is_seller, 
                           user_info=user_info, 
                           seller_reviews=seller_reviews, 
                           stock=stock,
                           current_page=page,
                           current_product_page=product_page,
                           total_pages=total_pages,
                           product_total_pages=product_total_pages,
                           mine = mine)


@bp.route('/vote-seller-review', methods=['POST'])
def vote_seller_review():
    data = request.get_json()
    review_id = data.get('review_id')
    vote_value = data.get('vote')

    # Get current helpfulness score and user’s existing vote
    helpfulness = Product.get_helpfulness(review_id)
    existing_vote = Product.get_user_vote(review_id, current_user.id)
    review = Review.get(review_id)

    if not review:
        return jsonify({'success': False, 'message': 'Review not found.'}), 404

    user_vote = 0
    if existing_vote is None:
        # No prior vote exists; create a new entry
        Review.add_vote(review_id, current_user.id, vote_value)
        helpfulness += vote_value
        user_vote = vote_value
    elif vote_value * existing_vote == -1:
        # User is changing their vote
        helpfulness -= 2 * existing_vote
        Review.update_vote(review_id, current_user.id, vote_value)
        user_vote = vote_value
    elif existing_vote == 0:
        # User has no prior vote; add the new vote
        Review.update_vote(review_id, current_user.id, vote_value)
        helpfulness += vote_value
        user_vote = vote_value
    else:
        # User toggles their vote off
        helpfulness -= existing_vote
        Review.update_vote(review_id, current_user.id, 0)
        user_vote = 0
    return jsonify({'success': True, 'new_helpfulness': helpfulness, 'user_vote': user_vote})


@bp.route('/update_stock', methods=['GET', 'POST'])
def update_stock():
    product_id = int(request.form['productID'])
    action = request.form['action']
    quantity = int(request.form['quantity'])
    sid = current_user.id
    Inventory.set_quantity(sid,product_id,quantity)
    return redirect(url_for('inventories.user'))






