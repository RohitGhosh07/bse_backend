from flask import Blueprint, jsonify, request
from models.models import db, Customer

otp_bp = Blueprint('otp_bp', __name__)

# Route to verify OTP
@otp_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    id = data.get('id')
    entered_otp = data.get('otp')
    
    if not id or not entered_otp:
        return jsonify({"error": "id and OTP are required"}), 400
    
    # Query the customer by phone number
    customer = Customer.query.filter_by(id=id).first()
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    # Check if the entered OTP matches the OTP saved for the customer
    if entered_otp == customer.otp:
        return jsonify({"message": "OTP verified successfully"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401
