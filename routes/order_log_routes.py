from collections import defaultdict
from flask import Blueprint, jsonify, request
from models.order_log_model import OrderLog, db
from models.models import Customer
from models.wallet import Wallet
from models.items import Item
from models.brand import Brand
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
        # Fetch order logs for the specific order
        order_logs = OrderLog.query.filter_by(order_id=order_id).order_by(OrderLog.order_placed_datetime.desc()).all()
    elif session_id:
        # Fetch order logs for the specific session
        order_logs = OrderLog.query.filter_by(session_id=session_id).order_by(OrderLog.order_placed_datetime.desc()).all()
    else:
        # Fetch all order logs if no order_id or session_id is provided
        order_logs = OrderLog.query.order_by(OrderLog.order_placed_datetime.desc()).all()

    # Create a dictionary to hold grouped order logs
    grouped_order_logs = defaultdict(lambda: {
        'id': None,
        'order_placed_datetime': None,
        'items': [],
        'order_id': None,
        'customer_id': None,
        'session_id': None,
        'total_invoice': 0,
        'total_items': 0,
        'brands': defaultdict(lambda: {
            'brand_id': None,
            'brand_image': None,
            'total_items': 0,
            'total_invoice': 0,  # Added field for total invoice per brand
        }),
    })

    for order_log in order_logs:
        # Fetch item details to get price and brand_id
        item = Item.query.get(order_log.item_id)
        if not item:
            continue

        item_price = item.base_price
        brand = Brand.query.get(item.brand_id)
        
        key = (order_log.order_id, order_log.order_placed_datetime)

        if grouped_order_logs[key]['id'] is None:
            grouped_order_logs[key]['id'] = order_log.id
            grouped_order_logs[key]['order_placed_datetime'] = order_log.order_placed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            grouped_order_logs[key]['order_id'] = order_log.order_id
            grouped_order_logs[key]['customer_id'] = order_log.customer_id
            grouped_order_logs[key]['session_id'] = order_log.session_id
            grouped_order_logs[key]['status'] = order_log.status

        # Append item details to the items list
        grouped_order_logs[key]['items'].append({
            'item_id': order_log.item_id,
            'quantity': order_log.quantity,
            'brand_id': brand.id if brand else None,
            'brand_image': brand.image if brand else None
        })

        # Calculate total invoice and total items per brand
        grouped_order_logs[key]['total_invoice'] += order_log.quantity * item_price
        grouped_order_logs[key]['total_items'] += order_log.quantity

        # Update brand details
        if brand:
            brand_group = grouped_order_logs[key]['brands'][brand.id]
            if brand_group['brand_id'] is None:
                brand_group['brand_id'] = brand.id
                brand_group['brand_image'] = brand.image
            brand_group['total_items'] += order_log.quantity
            brand_group['total_invoice'] += order_log.quantity * item_price  # Update brand's total invoice

    # Convert the brands defaultdict to a list
    for log in grouped_order_logs.values():
        log['brands'] = list(log['brands'].values())

    # Convert the grouped_order_logs defaultdict to a list
    serialized_order_logs = list(grouped_order_logs.values())

    return jsonify({'order_logs': serialized_order_logs}), 200

@order_logs_bp.route('/order_logs/update_status', methods=['PUT'])
def update_order_status():
    data = request.json
    order_id = data.get('order_id')
    item_ids = data.get('item_id')  # Can be a single ID or a list of IDs

    # Check if required fields are provided
    if not order_id or not item_ids:
        return jsonify({'error': 'Missing required fields'}), 400

    # Convert item_ids to a list if it's not already one
    if not isinstance(item_ids, list):
        item_ids = [item_ids]

    try:
        # Track updated items
        updated_items = []

        for item_id in item_ids:
            # Query the specific order log by order_id and item_id
            order_log = OrderLog.query.filter_by(order_id=order_id, item_id=item_id).first()
            if order_log is None:
                return jsonify({'error': f'Order log not found for item_id {item_id}'}), 404
            
            # Update the status to 'Completed'
            order_log.status = 'Completed'
            updated_items.append(item_id)

        # Commit the change to the database
        db.session.commit()

        return jsonify({
            'message': 'Order item status updated to Completed', 
            'order_id': order_id, 
            'updated_items': updated_items
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


