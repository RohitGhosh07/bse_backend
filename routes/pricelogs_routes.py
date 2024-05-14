# routes.py

from flask import Blueprint, request, jsonify
from models.priceLog import db, PriceLog

price_logs_bp = Blueprint('price_logs', __name__)

@price_logs_bp.route('/price_logs', methods=['GET'])
def get_price_logs():
    price_logs = PriceLog.query.all()
    serialized_price_logs = []
    for price_log in price_logs:
        serialized_price_log = {
            'item_id': price_log.item_id,
            'price': price_log.price,
            'market_date': price_log.market_date.strftime('%Y-%m-%d')
        }
        serialized_price_logs.append(serialized_price_log)
    return jsonify({'price_logs': serialized_price_logs}), 200


@price_logs_bp.route('/price_logs', methods=['POST'])
def create_price_logs():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Data must be provided as a list of JSON objects'}), 400

    for log_data in data:
        item_id = log_data.get('item_id')
        price = log_data.get('price')
        market_date = log_data.get('market_date')
        if not all([item_id, price, market_date]):
            return jsonify({'error': 'Missing required fields in one or more price logs'}), 400

        try:
            new_price_log = PriceLog(item_id=item_id, price=price, market_date=market_date)
            db.session.add(new_price_log)
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    try:
        db.session.commit()
        return jsonify({'message': 'Price logs created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

