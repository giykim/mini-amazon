from flask import render_template, request
from flask_login import current_user
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('index', __name__)


# @bp.route('/')
# def index():
#     # get all available products for sale:
#     products = Product.get_all(True)

#     # find k most expensive products:
#     expensive_products = Product.get_k_expensive(3)
        
#     # render the page by adding information to the index.html file
#     return render_template('index.html',
#                            avail_products=products,
#                            expensive_products=expensive_products
#                            )

@bp.route('/')
def index():
    # Get the current page number from the query parameters, defaulting to 1
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of products per page

    # Get paginated products for the current page
    avail_products = Product.get_available_products_paginated(page=page, per_page=per_page)

    # Calculate total pages based on the count of available products
    total_products = Product.count_available()  # A new function to count available products
    total_pages = (total_products + per_page - 1) // per_page  # Calculate the number of pages

    # Render the page by adding information to the index.html file
    return render_template(
        'index.html',
        avail_products=avail_products,
        page=page,
        total_pages=total_pages
    )

