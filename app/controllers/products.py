import os

from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.seller import Seller

from flask import Blueprint
bp = Blueprint('products', __name__)


# Make sure folder for images exists
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



@bp.route('/search', methods=['GET'])
def search():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page

    query = request.args.get('query')

    products = Product.search_products(query)

    # Get categories to choose from for filtering
    categories = Product.get_categories()

    # Toggle filter / sort menu
    toggle_filter = request.args.get('toggle_filter', False)

    # Get filter parameters
    max_price = request.args.get('max_price', float('inf'))
    if type(max_price) is str and len(max_price) < 1:
        max_price = float('inf')
    max_price = float(max_price)
    if max_price < float('inf'):
        max_price = round(max_price, 2)
        products = [product for product in products if product.price is not None and product.price <= max_price]

    min_rating = request.args.get('min_rating', 0)
    if type(min_rating) is str and len(min_rating) < 1:
        min_rating = 0
    min_rating = int(float(min_rating))
    products = [product for product in products if product.rating >= min_rating]

    category = request.args.get('category', '')
    if len(category) > 0:
        products = [product for product in products if product.category is not None and product.category == category]

    # Get search parameters
    sort_by = request.args.get('sort_by')
    arrow_direction = request.args.get('arrow_direction', 'down')
    reverse = arrow_direction == 'down'
    if sort_by is not None:
        if sort_by == "name":
            products = sorted(products, key=lambda product: product.name.lower(), reverse=(not reverse))
        elif sort_by == "price":
            products = sorted(
                products, 
                key=lambda product: product.price if product.price is not None else float('-inf'), 
                reverse=reverse
            )
        elif sort_by == "rating":
            products = sorted(products, key=lambda product: product.rating, reverse=reverse)

    # Calculate total pages based on the count of created products
    products_count = len(products)
    products = products[offset:offset+per_page]
    total_pages = (products_count + per_page - 1) // per_page  # Calculate the number of pages

    return render_template(
        'search.html',
        query=query,
        products_count=products_count,
        products=products,
        page=page,
        total_pages=total_pages,
        max_price=f"{max_price:.2f}",
        min_rating=min_rating,
        sort_by=sort_by,
        arrow_direction=arrow_direction,
        toggle_filter=toggle_filter,
        category=category,
        categories=categories,
        )


@bp.route('/product-page/<int:product_id>', methods=['GET'])
def product_page(product_id):
    # Reviews pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 3

    # Get info to display on product page
    product_info = Product.get_product_info(product_id)
    category = Product.get_product_category(product_id)
    tags = Product.get_product_tags(product_id)
    seller_info = Product.get_seller_info(product_id)
    creator_info = Product.get_creator_info(product_id)
    review_info = Product.get_reviews_paginated(product_id, page, per_page)
    total_reviews = Product.count_reviews(product_id)
    total_pages = (total_reviews + per_page - 1) // per_page

    # Get variables to display product rating
    ratings = Product.get_product_ratings(product_id)

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

    # Retrieve products related to current product
    related_products = Product.get_related_products(product_id)

    # If there is no creator associated with product
    if not creator_info:
        creator_info = [{'uid': -1, 'firstname': 'No', 'lastname': 'Creator'}]

    return render_template('product_page.html',
        product_info=product_info,
        category=category,
        tags=tags,
        seller_info=seller_info,
        creator_info=creator_info,
        review_info=review_info,
        total_pages=total_pages,
        current_page=page,
        user_votes=user_votes,
        has_bought=has_bought,
        is_seller=is_seller,
        ratings=ratings,
        related_products=related_products,
    )


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/new-product', methods=['POST'])
def new_product():
    """
    Route to create a new product
    """
    if current_user.is_authenticated:
        # Get values from form
        name = request.form.get('name')
        description = request.form.get('description')
        cid = request.form.get('category')
        tags = request.form.get('tags')

        image = request.files.get('image')
        if not image or not allowed_file(image.filename):
            flash('Invalid file format or no image uploaded.')
            return redirect(url_for('products.create_product'))
        
        # Attempt to insert a new product into Products relation
        pid, created = Product.new_product(name=name,
                                           description=description,
                                           uid=current_user.id,
                                           )
        
        # If the product name already exists or not valid image, the insert will fail
        if not created:
            flash("Product already exists or invalid image format.", "error")
        # If the product was successfully created, set the category
        else:
            # If user selected a cateogry
            if cid:
                Product.set_category(pid, cid)

            # If user added any tags
            for tag in tags.split(','):
                if len(tag) > 0:
                    Product.add_tag(pid=pid, tag=tag)

            # Get uploaded image file
            filename = f"image_{pid}.jpg"
            image.save(os.path.join(UPLOAD_FOLDER, filename))

        return redirect(url_for('products.product_page', product_id=pid))

    else:
        return redirect(url_for('index.index'))
    

@bp.route('/update-product', methods=['POST'])
def update_product():
    if current_user.is_authenticated:
        # Get values from form
        pid = request.form.get('pid')
        name = request.form.get('name')
        description = request.form.get('description')
        cid = request.form.get('category')
        tags = request.form.get('tags')

        image = request.files.get('image')
        if image:
            if not allowed_file(image.filename):
                flash('Invalid file format uploaded.')
                return redirect(url_for('products.update_product', pid=pid))
            else:
                # Get uploaded image file
                filename = f"image_{pid}.jpg"
                image.save(os.path.join(UPLOAD_FOLDER, filename))

        # Update product with new information
        Product.update_product(pid=pid, name=name, description=description)

        # If user selected a cateogry
        if cid:
            Product.set_category(pid=pid, cid=cid)
        # If not, remove category
        else:
            Product.remove_category(pid=pid)

        # Update tags
        # Remove all current tags
        Product.remove_all_tags(pid=pid)
        # Add all new tags
        for tag in tags.split(','):
            if len(tag) > 0:
                Product.add_tag(pid=pid, tag=tag)

        # Show user their update was successful
        flash("Successfully updated product info.", category="success")

        return redirect(url_for('products.product_page', product_id=pid))

    else:
        return redirect(url_for('index.index'))


@bp.route('/edit-product', methods=['GET'])
def edit_product():
    # Get product id from previous page
    pid = request.args.get('pid')

    # Get product information from id
    product = Product.get_product_info(pid)[0]

    # Get current product cateogry
    current_category = Product.get_product_category(pid)

    # Get current product tags
    current_tags = Product.get_product_tags(pid)

    # Get all categories for selecting product category
    categories = Product.get_categories()

    return render_template('edit_product.html',
                           product=product,
                           current_category=current_category,
                           current_tags=current_tags,
                           categories=categories
                           )


@bp.route('/create-product', methods=['GET'])
def create_product():
    """
    Route to form for creating a new product
    """
    categories = Product.get_categories()

    return render_template('create_product.html',
                           categories=categories,
                           )


@bp.route('/stock-product', methods=['GET'])
def stock_product():
    pid = request.args.get('product_id')
    product = Product.get_product_info(pid)[0]
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

