from flask import render_template, request
from flask_login import current_user
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review
from app.models.user import User
from app.models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('cart', __name__)


@bp.route('/cart', methods=['POST', 'GET'])
def cart():
    if current_user.is_authenticated:
        # Adding products to cart from product page
        product_id = request.form.get('product_id')
        seller_id = request.form.get('seller_id')
        quantity = request.form.get('quantity')

        # Changing product quantity from cart page
        old_quantity = request.form.get('old_quantity')
        new_quantity = request.form.get('new_quantity')

        # Remove product
        remove_product_id = request.form.get('remove_product_id')

        if quantity is not None:
            Purchase.add_to_cart(current_user.id, product_id, seller_id, quantity)
        elif new_quantity is not None:
            new_quantity = int(new_quantity)
            new_quantity -= int(old_quantity)
            Purchase.add_to_cart(current_user.id, product_id, seller_id, new_quantity)
        elif remove_product_id is not None:
            Purchase.remove_product(current_user.id, remove_product_id, seller_id)

        cart = Purchase.get_cart(current_user.id)
    else:
        cart = []
    max_q = []
    for p in cart:
        max_q.append(Product.get_seller_quant(p[0],p[1])[0][0])
    total = sum(item.price * item.quantity for item in cart)
    total = float(total)

    return render_template('cart.html', cart=cart, total=total, max_q = max_q)


@bp.route('/checkout', methods=['GET'])
def checkout():
    if current_user.is_authenticated:
        user = User.get(current_user.id)
        cart = Purchase.get_cart(current_user.id)
    else:
        user = None
        cart = []
    
    total = sum(item.price * item.quantity for item in cart)
    total = float(total)

    return render_template('checkout.html', user=user, total=total)

@bp.route('/place-order', methods=['POST'])
def place_order():
    total = 0

    if current_user.is_authenticated:
        cart = Purchase.get_cart(current_user.id)

        total = sum(item.price * item.quantity for item in cart)
        total = float(total)

        for item in cart:
            Purchase.order_product(current_user.id, item.id, item.sid)

        user = User.get(current_user.id)
        User.update_balance(user.id, user.balance - round(total * 1.075, 2))
    else:
        user = None
        cart = []

    return render_template('order_placed.html')
