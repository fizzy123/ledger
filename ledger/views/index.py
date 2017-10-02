import logging
from datetime import datetime
from sqlalchemy import func
from flask import Blueprint, jsonify, request

from ledger import db
from ledger.models import Transaction
from .decorators import auth_required

logger = logging.getLogger(__name__)

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=['GET'])
@auth_required
def balances_view():
    # Get the date provided in the args or use the current date
    if request.args.get('date'):
        date = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    else:
        date = datetime.now()

    totals = db.session.query(Transaction.recipiant,
                              func.sum(Transaction.amount)) \
                        .filter(Transaction.date <= date) \
                        .group_by(Transaction.recipiant) \
                        .all()

    # Put the query results into a more comfortable format
    totals_dict = {}
    for total in totals:
        totals_dict[total[0]] = round(total[1], 2)
    return jsonify(totals_dict)
