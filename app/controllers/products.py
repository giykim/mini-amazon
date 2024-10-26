from flask import render_template, request
from flask_login import current_user
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