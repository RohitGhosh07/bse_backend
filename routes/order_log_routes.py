from flask import Blueprint, jsonify, request
from models.order_log_model import OrderLog, db
from models.models import Customer
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
        
        # Use customer phone and current timestamp as session_id
        session_id = customer.phone + str(order_placed_datetime)[:20 - len(customer.phone)]
        
        # Create the order ID serially
        last_order = OrderLog.query.order_by(OrderLog.id.desc()).first()
        if last_order:
            order_id = last_order.order_id + 1
        else:
            order_id = 1

        # Create order logs for each item in the array
        for item in data['items']:
            item_id = item.get('id')
            quantity = item.get('count')
            if item_id is None or quantity is None:
                return jsonify({'error': 'Invalid item data in array'}), 400
            
            new_order_log = OrderLog(
                order_placed_datetime=order_placed_datetime,
                item_id=item_id,
                quantity=quantity,
                order_id=order_id,
                customer_id=customer_id,
                session_id=session_id
            )
            db.session.add(new_order_log)
        
        db.session.commit()
        return jsonify({'message': 'Ordered successfully', 'order_id': order_id, 'session_id': session_id}), 201
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

    serialized_order_logs = []
    for order_log in order_logs:
        serialized_order_log = {
            'id': order_log.id,
            'order_placed_datetime': order_log.order_placed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'item_id': order_log.item_id,
            'quantity': order_log.quantity,
            'order_id': order_log.order_id,
            'customer_id': order_log.customer_id,
            'session_id': order_log.session_id,
        }
        serialized_order_logs.append(serialized_order_log)

    return jsonify({'order_logs': serialized_order_logs}), 200

