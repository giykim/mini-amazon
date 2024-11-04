from flask import render_template, request, jsonify
from flask_login import current_user
from app import db
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('products', __name__)


@bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    products = Product.search_products(query)

    return render_template('search.html', query=query, products=products)


@bp.route('/product-page/<int:product_id>', methods=['GET'])
def product_page(product_id):
    product_info = Product.get_product_info(product_id)
    seller_info = Product.get_seller_info(product_id)
    review_info = Product.get_review_info(product_id)

    return render_template('product_page.html', product_info=product_info, seller_info=seller_info, review_info=review_info)

@bp.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    review_id = data.get('review_id')
    vote_value = data.get('vote')
    # Fetch current helpfulness
    helpfulness = Product.get_helpfulness(review_id)
    # Check for existing vote for this user-review pair
    existing_vote = Product.get_user_vote(review_id, current_user.id)
    print(helpfulness)
    print(existing_vote)

    if (vote_value == 1 and existing_vote == 1) or (vote_value == -1 and existing_vote == -1):
        return jsonify({'success': False, 'message' : 'You have voted on this review already.'}), 400

    # Retrieve review by ID
    review = Product.get_review_by_id(review_id)
    if not review:
        return jsonify({'success': False, 'message': 'Review not found.'}), 404
    
    user_vote = 0
    if existing_vote is not None: 
        if existing_vote == 0: 
            # User current vote is 0
            Product.update_vote(review_id, current_user.id, vote_value)
            helpfulness += vote_value
            user_vote = vote_value 
        else: 
            # User changes vote from upvote to downvote or vice versa
            helpfulness += vote_value
            Product.update_vote(review_id, current_user.id, 0)
            user_vote = 0
    else:
        # No prior vote exists; create a new entry
        Product.add_vote(review_id, current_user.id, vote_value)
        helpfulness += vote_value
        user_vote = vote_value
    
    return jsonify({'success': True, 'new_helpfulness': helpfulness, 'user_vote': user_vote})

