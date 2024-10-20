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