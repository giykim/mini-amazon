from flask import render_template, request
from flask_login import current_user
import datetime

from app.models.inventory import Inventory
from app.models.seller import Seller
from app.models.product import Product
from app.models.user import User


from flask import Blueprint
bp = Blueprint('inventories', __name__)

@bp.route('/stock', methods = ['GET'])
def get_stock():
    sid = request.args.get('sid')
    if Seller.get(sid) == None:
        return "Not valid"
    pids = Inventory.get_inventory(sid)
    stocked = []
    print(pids)
    for p in pids:
        stocked.append(Inventory.get_product_detail(p[0],sid))
    print(True)
    print(stocked)
    return render_template('stock.html', sid=sid, stocked=stocked)




