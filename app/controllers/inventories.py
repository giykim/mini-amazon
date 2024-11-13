from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app import db
import json
import datetime

from app.models.inventory import Inventory
from app.models.seller import Seller
from app.models.product import Product
from app.models.user import User
from app.models.reviews import Review


from flask import Blueprint
bp = Blueprint('inventories', __name__)

@bp.route('/stock', methods = ['GET'])
def get_stock():
    sid = request.args.get('sid')
    
    seller = Seller.get(sid)
    if seller is None:
        is_seller = False
    else:
        is_seller = True

    if current_user.is_authenticated and str(sid) == str(current_user.id) and is_seller: 
        return redirect(url_for('inventories.get_s_info'))
    
    # for reviews
    page = request.args.get('page', 1, type=int)
    per_page = 3

    # for products sold by
    product_page = request.args.get('product_page', 1, type=int)
    product_per_page = 9

    
    
    user_info = User.get(sid) if is_seller else None

    # retrieving paginated reviews
    total_reviews = Review.count_seller_reviews(sid) if is_seller else 0
    total_pages = (total_reviews + per_page - 1) // per_page
    seller_reviews = Review.get_seller_reviews_paginated(sid, page, per_page) if is_seller else None

    # retrieving paginated products
    total_products = Inventory.count_sold_products(sid) if is_seller else 0
    product_total_pages = (total_products + product_per_page - 1) // product_per_page
    stocked = None

    if is_seller: 
        stocked = Inventory.get_sold_by_details_paginated(sid, product_page, product_per_page)
    
    # pids = Inventory.get_inventory(sid)
    # stocked = []
    # for p in pids:
    #     stocked.append(Inventory.get_product_detail(p[0],sid))
    return render_template('stock.html', 
                           sid=sid, 
                           is_seller=is_seller, 
                           user_info=user_info, 
                           seller_reviews=seller_reviews, 
                           stocked=stocked,
                           current_page=page,
                           current_product_page=product_page,
                           total_pages=total_pages,
                           product_total_pages=product_total_pages,
                           mine = False)

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

@bp.route('/my_inventory', methods = ['GET','POST'])
def get_s_info():
    sid = current_user.id
    # for reviews
    page = request.args.get('page', 1, type=int)
    per_page = 3

    # for products sold by
    product_page = request.args.get('product_page', 1, type=int)
    product_per_page = 9

    seller = Seller.get(sid)
    if seller is None:
        is_seller = False
    else:
        is_seller = True
    
    user_info = User.get(sid) if is_seller else None

    # retrieving paginated reviews
    total_reviews = Review.count_seller_reviews(sid) if is_seller else 0
    total_pages = (total_reviews + per_page - 1) // per_page
    seller_reviews = Review.get_seller_reviews_paginated(sid, page, per_page) if is_seller else None

    # retrieving paginated products
    total_products = Inventory.count_sold_products(sid) if is_seller else 0
    product_total_pages = (total_products + product_per_page - 1) // product_per_page
    stocked = None

    if is_seller: 
        if current_user.is_authenticated and str(sid) == str(current_user.id):
            # Display the seller's full inventory if `sid` matches current user ID
            stocked = Inventory.get_inventory_details(sid)
    
    # pids = Inventory.get_inventory(sid)
    # stocked = []
    # for p in pids:
    #     stocked.append(Inventory.get_product_detail(p[0],sid))
    return render_template('stock.html', 
                           sid=sid, 
                           is_seller=is_seller, 
                           user_info=user_info, 
                           seller_reviews=seller_reviews, 
                           stocked=stocked,
                           current_page=page,
                           current_product_page=product_page,
                           total_pages=total_pages,
                           product_total_pages=product_total_pages,
                           mine = True)

@bp.route('/update_stock', methods=['GET', 'POST'])
def update_stock():
    product_id = int(request.form['productID'])
    action = request.form['action']
    quantity = int(request.form['quantity'])
    Inventory.set_quantity(product_id,current_user.id,quantity)
    return redirect(url_for('inventories.get_s_info'))






