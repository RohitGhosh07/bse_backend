from datetime import datetime
from flask import Blueprint, jsonify, request
from models.models import Customer
from models.wallet import Wallet, db  # Import Wallet model and db
from flask_cors import CORS

wallets_bp = Blueprint('wallets_bp', __name__)
CORS(wallets_bp)  # Enable CORS for all routes

@wallets_bp.route("/wallets", methods=["GET"])
def get_wallets():
    customer_id = request.args.get('customer_id')
    session_id = request.args.get('session_id')
    phone = request.args.get('phone')

    try:
        if phone:
            wallets = Wallet.query.filter_by(phone=phone).all()
        elif session_id:
            wallets = Wallet.query.filter_by(session_id=session_id).all()
        elif customer_id:
            wallets = Wallet.query.filter_by(customer_id=customer_id).all()
        else:
            wallets = Wallet.query.all()

        if wallets:
            wallet_list = [
                {
                    'id': wallet.id,
                    'created_at': wallet.created_at,
                    'customer_id': wallet.customer_id,
                    'amount_loaded': wallet.amount_loaded,
                    'session_id': wallet.session_id,
                    'current_amount': wallet.current_amount
                } for wallet in wallets
            ]
            return jsonify({"wallets": wallet_list})
        else:
            return jsonify({"error": "No wallets found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@wallets_bp.route("/wallets", methods=["POST"])
def add_wallets():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Invalid JSON data format. Expected an array of wallets."}), 400

    response_data = []

    for wallet_data in data:
        phone_number = wallet_data.get('phone_number')
        amount_loaded = wallet_data.get('amount_loaded')

        if not phone_number or amount_loaded is None:
            return jsonify({"error": "Incomplete data in one of the wallets."}), 400

        # Fetch customer by phone number
        customer = Customer.query.filter_by(phone=phone_number).order_by(Customer.id.desc()).first()
        if not customer:
            return jsonify({"error": f"No customer found with phone number {phone_number}"}), 404

        customer_id = customer.id

        # Create session_id using phone number and today's date
        order_placed_datetime = datetime.utcnow()
        formatted_date = order_placed_datetime.strftime("%Y%m%d")
        session_id = phone_number + formatted_date

        # Fetch the latest wallet for the customer
        wallet = Wallet.query.filter_by(customer_id=customer_id).order_by(Wallet.id.desc()).first()

        if wallet:
            # Update existing wallet
            wallet.current_amount += amount_loaded
            wallet.session_id = session_id
        else:
            # Create a new wallet if it doesn't exist
            wallet = Wallet(
                customer_id=customer_id,
                amount_loaded=amount_loaded,
                session_id=session_id,
                current_amount=amount_loaded
            )

        try:
            db.session.add(wallet)
            db.session.commit()
            response_data.append({
                'customer_id': customer_id,
                'current_amount': wallet.current_amount,
                'session_id': session_id
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred while adding a wallet: {str(e)}"}), 500

    return jsonify({"message": "Wallets updated successfully", "wallets": response_data}), 201

# @wallets_bp.route("/wallets/<int:id>", methods=["PUT"])
# def update_wallet(id):
#     wallet = Wallet.query.get_or_404(id)
#     data = request.get_json()
    
#     wallet.amount_loaded = data.get('amount_loaded', wallet.amount_loaded)
#     wallet.current_amount = data.get('current_amount', wallet.current_amount)
    
#     db.session.commit()
#     return jsonify({'message': 'Wallet updated successfully'})
@wallets_bp.route("/wallets/<session_id>", methods=["PUT"])
def update_wallet(session_id):
    wallet = Wallet.query.filter_by(session_id=session_id).first_or_404()
    data = request.get_json()
    
    if 'current_amount' in data:
        wallet.current_amount = data['current_amount']
    else:
        return jsonify({'error': 'current_amount is required'}), 400
    
    try:
        db.session.commit()
        return jsonify({'message': 'Wallet updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
