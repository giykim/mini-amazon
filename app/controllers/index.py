from flask import render_template
from flask_login import current_user
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all(True)

    # find k most expensive products:
    expensive_products = Product.get_k_expensive(3)
        
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           expensive_products=expensive_products
                           )
