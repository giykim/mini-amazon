from flask import render_template, request
from flask_login import current_user
import datetime

from app.models.inventory import Inventory
from app.models.seller import Seller
from app.models.product import Product
from app.models.user import User
from app.models.reviews import Review


from flask import Blueprint
bp = Blueprint('inventories', __name__)

@bp.route('/stock', methods = ['GET'])
def get_stock():
    sid = request.args.get('sid')
    seller = Seller.get(sid)
    if seller is None:
        is_seller = False
    else:
        is_seller = True
    
    user_info = User.get(sid) if is_seller else None

    seller_reviews = Review.get_seller_reviews(sid) if is_seller else None

    if is_seller: 
        if str(sid) == str(current_user.id):
            # Display the seller's full inventory if `sid` matches current user ID
            stocked = Inventory.get_inventory_details(sid)  # Retrieves full inventory
        else:
            # Display only products actively sold by the seller if `sid` is different
            stocked = Inventory.get_sold_by_details(sid)  # Retrieves only items from `SoldBy` table
    else: 
        stocked = None
    
    # pids = Inventory.get_inventory(sid)
    # stocked = []
    # for p in pids:
    #     stocked.append(Inventory.get_product_detail(p[0],sid))
    return render_template('stock.html', sid=sid, is_seller=is_seller, user_info=user_info, seller_reviews=seller_reviews, stocked=stocked)

