from flask import Blueprint, jsonify, request
from models.wallet import Wallet, db  # Import Wallet model and db
from flask_cors import CORS

wallets_bp = Blueprint('wallets_bp', __name__)
CORS(wallets_bp)  # Enable CORS for all routes

@wallets_bp.route("/wallets", methods=["GET"])
def get_wallets():
    wallet_id = request.args.get('id')
    customer_id = request.args.get('customer_id')

    if wallet_id:
        wallets = Wallet.query.filter_by(id=wallet_id).all()
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

@wallets_bp.route("/wallets", methods=["POST"])
def add_wallets():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Invalid JSON data format. Expected an array of wallets."}), 400

    response_data = []

    for wallet_data in data:
        customer_id = wallet_data.get('customer_id')
        amount_loaded = wallet_data.get('amount_loaded')
        session_id = wallet_data.get('session_id')
        current_amount = wallet_data.get('current_amount')

        if not customer_id or not amount_loaded or not session_id or not current_amount:
            return jsonify({"error": "Incomplete data in one of the wallets."}), 400

        new_wallet = Wallet(
            customer_id=customer_id,
            amount_loaded=amount_loaded,
            session_id=session_id,
            current_amount=current_amount
        )

        try:
            db.session.add(new_wallet)
            db.session.commit()
            response_data.append({
                'id': new_wallet.id,
                'created_at': new_wallet.created_at,
                'customer_id': new_wallet.customer_id,
                'amount_loaded': new_wallet.amount_loaded,
                'session_id': new_wallet.session_id,
                'current_amount': new_wallet.current_amount
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred while adding a wallet: {str(e)}"}), 500

    return jsonify({"message": "Wallets added successfully", "wallets": response_data}), 201

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
