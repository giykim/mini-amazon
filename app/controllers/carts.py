from flask import render_template, request
from flask_login import current_user
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('cart', __name__)


@bp.route('/cart', methods=['POST', 'GET'])
def cart():
    if current_user.is_authenticated:
        product_id = request.form.get('product_id')
        seller_id = request.form.get('seller_id')
        quantity = request.form.get('quantity')

        if quantity is not None:
            Purchase.add_to_cart(current_user.id, product_id, seller_id, quantity)

        cart = Purchase.get_cart(current_user.id)
    else:
        cart = []
    
    total = sum(item.price for item in cart)

    return render_template('cart.html', cart=cart, total=total)
