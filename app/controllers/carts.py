from flask import render_template, request
from flask_login import current_user
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('cart', __name__)


@bp.route('/cart', methods=['GET'])
def cart():
    if current_user.is_authenticated:
        # find the products current user has in cart:
        cart = Purchase.get_cart(current_user.id)

    else:
        cart = None

    return render_template('cart.html', cart=cart)