from collections import defaultdict
from flask import Blueprint, jsonify, request
from models.order_log_model import OrderLog, db
from models.models import Customer
from models.wallet import Wallet
from models.items import Item
from datetime import datetime

order_logs_bp = Blueprint('order_logs', __name__)

@order_logs_bp.route('/order_logs', methods=['POST'])
def create_order_log():
    data = request.json
    order_placed_datetime = datetime.utcnow()  # Get the current UTC datetime
    customer_id = data.get('customer_id')
    
    # Check for required fields
    if not all([customer_id, 'items' in data]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Fetch customer by customer_id
        customer = Customer.query.get(customer_id)
        if customer is None:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Check if customer phone is available
        if not customer.phone:
            return jsonify({'error': 'Customer phone number is missing'}), 400
        
        # Retrieve session_id from customer model
        session_id = customer.session_id

        # Create the order ID serially
        last_order = OrderLog.query.order_by(OrderLog.id.desc()).first()
        if last_order:
            order_id = last_order.order_id + 1
        else:
            order_id = 1

        # Create order logs for each item in the array
        total_amount = 0  # Initialize total amount
        for item in data['items']:
            item_id = item.get('id')
            quantity = item.get('count')
            if item_id is None or quantity is None:
                return jsonify({'error': 'Invalid item data in array'}), 400
            
            # Fetch item by item_id
            item = Item.query.get(item_id)
            if item is None:
                return jsonify({'error': 'Item not found'}), 404
            
            # Calculate item amount and add to total amount
            item_amount = item.base_price * quantity
            total_amount += item_amount
            
            new_order_log = OrderLog(
                order_placed_datetime=order_placed_datetime,
                item_id=item_id,
                quantity=quantity,
                order_id=order_id,
                customer_id=customer_id,
                session_id=session_id
            )
            db.session.add(new_order_log)
        
        # Fetch wallet by customer_id
        wallet = Wallet.query.filter_by(customer_id=customer_id).first()
        if wallet is None:
            return jsonify({'error': 'Customer wallet not found'}), 404

        # Check if wallet has sufficient balance
        if wallet.current_amount < total_amount:
            return jsonify({'error': 'Insufficient wallet balance'}), 400

        # Deduct total amount from wallet
        wallet.current_amount -= total_amount
        db.session.commit()

        wallet_data = {
            'balance': wallet.current_amount,
        }

        return jsonify({'message': 'Ordered successfully', 'order_id': order_id, 'session_id': session_id, 'total_amount': total_amount, 'wallet': wallet_data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



    

@order_logs_bp.route('/order_logs', methods=['GET'])
def get_order_logs():
    # Check if order_id or session_id parameter is present in the request
    order_id = request.args.get('order_id')
    session_id = request.args.get('session_id')

    if order_id:
        # If order_id is provided, fetch order logs for that specific order
        order_logs = OrderLog.query.filter_by(order_id=order_id).order_by(OrderLog.order_placed_datetime.desc()).all()
    elif session_id:
        # If session_id is provided, fetch order logs for that specific session
        order_logs = OrderLog.query.filter_by(session_id=session_id).order_by(OrderLog.order_placed_datetime.desc()).all()
    else:
        # If no order_id or session_id provided, fetch all order logs
        order_logs = OrderLog.query.order_by(OrderLog.order_placed_datetime.desc()).all()

    grouped_order_logs = defaultdict(lambda: {
        'id': None,
        'order_placed_datetime': None,
        'items': [],
        'order_id': None,
        'customer_id': None,
        'session_id': None
    })

    for order_log in order_logs:
        key = (order_log.order_id, order_log.order_placed_datetime)
        if grouped_order_logs[key]['id'] is None:
            grouped_order_logs[key]['id'] = order_log.id
            grouped_order_logs[key]['order_placed_datetime'] = order_log.order_placed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            grouped_order_logs[key]['order_id'] = order_log.order_id
            grouped_order_logs[key]['customer_id'] = order_log.customer_id
            grouped_order_logs[key]['session_id'] = order_log.session_id
        
        grouped_order_logs[key]['items'].append({
            'item_id': order_log.item_id,
            'quantity': order_log.quantity
        })

    serialized_order_logs = list(grouped_order_logs.values())

    return jsonify({'order_logs': serialized_order_logs}), 200

