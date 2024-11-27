import copy

from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user

from app.models.inventory import Inventory
from app.models.seller import Seller
from app.models.purchase import Purchase
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

    # Get info of user
    user_info = User.get(uid)
    
    # Check if user is a seller
    seller = Seller.get(uid)
    if seller is None:
        is_seller = False
    else:
        is_seller = True
    
    # Review pagination parameters
    reviews_page = request.args.get('reviews_page', 1, type=int)
    reviews_per_page = 3

    # Retrieve paginated reviews
    reviews_count = Review.count_seller_reviews(uid) if is_seller else 0
    reviews_total_pages = (reviews_count + reviews_per_page - 1) // reviews_per_page
    seller_reviews = Review.get_seller_reviews_paginated(uid, reviews_page, reviews_per_page) if is_seller else None

    # Get product info corresponding to seller
    if is_seller:
        # Check if current user has bought from this seller
        has_bought = Purchase.has_bought_from(uid=current_user.id, sid=uid)

        # Get ratings for seller
        ratings = Seller.get_seller_ratings(sid=uid)

        # Get products that are up for sale
        selling = Inventory.get_selling(uid)

        # Get incoming orders
        incoming_purchases = Purchase.get_incoming_purchases(uid)

        # Get products that are in inventory (even if they may not be on sale)
        stock = Inventory.get_inventory_details(uid)
    else:
        has_bought = False
        ratings = None
        selling = None
        incoming_purchases = None
        stock = None

    # Get products created by user
    selling_page = request.args.get('selling_page', 1, type=int)
    selling_per_page = 9
    selling_offset = (selling_page - 1) * selling_per_page
    
    selling_count = len(selling) if selling else 0
    selling = selling[selling_offset:selling_offset+selling_per_page] if selling else 0

    # Calculate total pages based on the count of created products
    selling_total_pages = (selling_count + selling_per_page - 1) // selling_per_page  # Calculate the number of pages

    # Get products created by user
    created_products_page = request.args.get('created_products_page', 1, type=int)
    created_products_per_page = 9
    created_products_offset = (created_products_page - 1) * created_products_per_page

    all_products = Product.get_user_products(uid)
    created_products_products_count = len(all_products)
    created_products = all_products[created_products_offset:created_products_offset+created_products_per_page]

    # Calculate total pages based on the count of created products
    created_products_total_pages = (created_products_products_count + created_products_per_page - 1) // created_products_per_page  # Calculate the number of pages

    # Check if user is looking at their own profile
    mine = False
    if current_user.is_authenticated:
        mine = (current_user.id == int(uid))

    return render_template('user.html', 
                           uid=uid, 
                           is_seller=is_seller, 
                           user_info=user_info, 
                           has_bought=has_bought,
                           mine=mine,

                           created_products=created_products,
                           created_products_page=created_products_page,
                           created_products_total_pages=created_products_total_pages,

                           ratings=ratings,
                           seller_reviews=seller_reviews, 
                           reviews_page=reviews_page,
                           reviews_total_pages=reviews_total_pages,

                           selling=selling,
                           selling_page=selling_page,
                           selling_total_pages=selling_total_pages,
                           
                           incoming_purchases=incoming_purchases,
                           stock=stock,
                           )


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


@bp.route('/update-stock', methods=['POST'])
def update_stock():
    # Get parameters from method call
    id = current_user.id
    pid = request.form.get('product_id')
    quantity = request.form.get('quantity')

    # Update row associated with seller and product by adding quantity
    Inventory.update_stock(id, pid, quantity)

    return redirect(url_for('inventories.get_user', uid=current_user.id, page=1))


@bp.route('/update-sold-by', methods=['POST'])
def update_sold_by():
    # Get parameters from method call
    id = current_user.id
    pid = request.form.get('product_id')
    quantity = request.form.get('quantity')
    price = request.form.get('price')

    # Update row associated with seller and product by adding quantity
    Inventory.update_sold_by(id, pid, quantity, price)

    return redirect(url_for('inventories.get_user', uid=current_user.id, page=1))


@bp.route('/fulfill-order', methods=['POST'])
def fulfill_order():
    # Get parameters from method call
    pid = request.form.get('product_id')
    sid = request.form.get('seller_id')
    uid = request.form.get('user_id')
    price = request.form.get('price')
    time_purchased = request.form.get('time_purchased')

    # Update row fulfilled column for purchase
    success = Inventory.fulfill_order(pid, sid, uid, time_purchased, price)

    # If order could not be fulfilled because of lack of inventory quantity
    if not success:
        flash('Could not fulfill order due to not enough product in stock!', 'error')
    else:
        flash('Successfully fulfilled order!')

    return redirect(url_for('inventories.get_user', uid=current_user.id, page=1))
