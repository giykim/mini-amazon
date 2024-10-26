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
        print(product_id, seller_id, quantity)
        if quantity is not None:
            Purchase.add_to_cart(current_user.id, product_id, seller_id, quantity)

        cart = Purchase.get_cart(current_user.id)
    else:
        cart = []
    
    total = sum(item.price for item in cart)

    return render_template('cart.html', cart=cart, total=total)



# @bp.route('/cart', methods=['GET'])
# def add_to_cart(product_id, seller_id, price):
#     if current_user.is_authenticated:
#         cart = Purchase.get_cart(current_user.id)

#         quantity = request.args.get('quantity')
#         if quantity is not None:
#             # add to cart
#             pass
#     else:
#         cart = []
    
#     total = 0
#     for item in cart:
#         total += item.price

#     return render_template('cart.html', cart=cart, total=total)
