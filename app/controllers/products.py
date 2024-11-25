from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.seller import Seller

from flask import Blueprint
bp = Blueprint('products', __name__)


@bp.route('/search', methods=['GET'])
def search():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page

    query = request.args.get('query')

    all_products = Product.search_products(query)
    products_count = len(all_products)
    products = all_products[offset:offset+per_page]

    # Calculate total pages based on the count of created products
    total_pages = (products_count + per_page - 1) // per_page  # Calculate the number of pages

    return render_template(
        'search.html',
        query=query,
        products_count=products_count,
        products=products,
        page=page,
        total_pages=total_pages
        )


@bp.route('/product-page/<int:product_id>', methods=['GET'])
def product_page(product_id):
    # Reviews pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 3

    # Get info to display on product page
    product_info = Product.get_product_info(product_id)
    seller_info = Product.get_seller_info(product_id)
    creator_info = Product.get_creator_info(product_id)
    review_info = Product.get_reviews_paginated(product_id, page, per_page)
    total_reviews = Product.count_reviews(product_id)
    total_pages = (total_reviews + per_page - 1) // per_page

    # Check if the user is a seller (to allow them to stock this product)
    if current_user.is_authenticated:
        id = current_user.id
    else:
        id = -1

    seller = Seller.get(id)
    if seller is None:
        is_seller = False
    else:
        is_seller = True

    # Check if the user has bought the product
    if current_user.is_authenticated:
        has_bought = Product.has_bought(current_user.id, product_id)
        user_votes = Product.get_user_votes_for_product(product_id, current_user.id)
    else:
        has_bought = False
        user_votes = None

    # If there is no creator associated with product
    if not creator_info:
        creator_info = [{'uid': -1, 'firstname': 'No', 'lastname': 'Creator'}]

    return render_template('product_page.html',
        product_info=product_info,
        seller_info=seller_info,
        creator_info=creator_info,
        review_info=review_info,
        total_pages=total_pages,
        current_page=page,
        user_votes=user_votes,
        has_bought=has_bought,
        is_seller=is_seller
    )


@bp.route('/new-product', methods=['POST'])
def new_product():
    if current_user.is_authenticated:
        name = request.form.get('name')
        description = request.form.get('description')
        pid, created = Product.new_product(name=name, description=description, uid=current_user.id)

        if not created:
            flash("Product already exists.", "error")

        return redirect(url_for('products.product_page', product_id=pid))

    else:
        return redirect(url_for('index.index'))
    

@bp.route('/update-product', methods=['POST'])
def update_product():
    if current_user.is_authenticated:
        pid = request.form.get('pid')
        name = request.form.get('name')
        description = request.form.get('description')

        Product.update_product(pid=pid, name=name, description=description)

        flash("Successfully updated product info.", "error")

        return redirect(url_for('products.product_page', product_id=pid))

    else:
        return redirect(url_for('index.index'))


@bp.route('/edit-product', methods=['GET'])
def edit_product():
    pid = request.args.get('pid')
    product = Product.get_product_info(pid)[0]
    return render_template('edit_product.html', product=product)


@bp.route('/create-product', methods=['GET'])
def create_product():
    return render_template('create_product.html')


@bp.route('/stock-product', methods=['GET'])
def stock_product():
    pid = request.args.get('product_id')
    product = Product.get_product_info(pid)[0]
    print(product.id)
    return render_template('stock_product.html', product=product)


@bp.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    review_id = data.get('review_id')
    vote_value = data.get('vote')
    # Fetch current helpfulness
    helpfulness = Product.get_helpfulness(review_id)
    # Check for existing vote for this user-review pair
    existing_vote = Product.get_user_vote(review_id, current_user.id)
    # Retrieve review by ID
    review = Product.get_review_by_id(review_id)
    if not review:
        return jsonify({'success': False, 'message': 'Review not found.'}), 404
    
    user_vote = 0
    if existing_vote is None: 
        # No prior vote exists; create a new entry
        Product.add_vote(review_id, current_user.id, vote_value)
        helpfulness += vote_value
        user_vote = vote_value
    elif vote_value * existing_vote == -1: 
        # If they change their vote 
        helpfulness -= 2*existing_vote
        Product.update_vote(review_id, current_user.id, vote_value)
        user_vote = vote_value
    elif existing_vote == 0: 
        # Voted before, but currently has no vote value
        Product.update_vote(review_id, current_user.id, vote_value)
        helpfulness += vote_value
        user_vote = vote_value
    else: 
        # If they toggle their vote off
        helpfulness -= existing_vote
        Product.update_vote(review_id, current_user.id, 0)
        user_vote = 0
        
    return jsonify({'success': True, 'new_helpfulness': helpfulness, 'user_vote': user_vote})

