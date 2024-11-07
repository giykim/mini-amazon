from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app import db
import json
import datetime

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.reviews import Review

from flask import Blueprint
bp = Blueprint('social', __name__)


@bp.route('/product-review', methods=['GET'])
def product_review():
    product_id = request.args.get('product_id')

    product = Product.search_products(product_id)

    return render_template('product_review.html', product=product)
