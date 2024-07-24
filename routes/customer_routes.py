from flask import Blueprint, jsonify, request
from models.models import db, Customer
import random
import requests
import urllib.parse

customer_bp = Blueprint('customer_bp', __name__)

def send_sms_new(DLT_TE_ID, sms_mob_no, sms_message):
    authkey = "360681AWirElvLuXvn609e3f14P1"
    sender = "FRCPWR"
    route = "4"
    country = "91"
    sms_message = sms_message
    uri = (
        "http://bulksms.smslive.in/api/sendhttp.php?"
        "authkey={}&DLT_TE_ID={}&mobiles={}&message={}&sender={}&route={}&country={}"
    ).format(
        authkey,
        DLT_TE_ID,
        sms_mob_no,
        urllib.parse.quote(sms_message),
        sender,
        route,
        country,
    )
    response = requests.get(uri)
    return response

# Route to get all customers
@customer_bp.route("/customers", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    customer_list = [
        {'id': customer.id, 'name': customer.name, 'phone': customer.phone, 'otp': customer.otp, 'created_at': customer.created_at} for customer in customers
    ]
    return jsonify({"customers": customer_list})

# Route to add a new customer
@customer_bp.route("/customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400
    
    name = data.get('name', None)  # Set name to None if not provided
    new_customer = Customer(name=name, phone=phone)
    
    try:
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices('0123456789', k=6))
        # Save OTP to the new customer object
        new_customer.otp = otp

        # Print the OTP value for debugging
        print("Generated OTP:", otp)
        
        # Add the new customer to the session
        db.session.add(new_customer)
        
        # Commit the session to save the new customer and OTP to the database
        db.session.commit()

        # Send OTP to the provided phone number
        DLT_TE_ID = "1307162133541247932"  # Set your DLT_TE_ID here
        sms_message = f"Your One Time Password for BSE is {otp}. Put this OTP and press submit. Team Force Power Infotech Pvt Ltd"
        response = send_sms_new(DLT_TE_ID, phone, sms_message)

        # Log the complete response for debugging
        print("SMS API Response Status Code:", response)
        print("SMS API Response Text:", response.text)

        if response.status_code == 200 :
            print("Message sent successfully.")
            return jsonify({"message": "OTP sent successfully", "id": new_customer.id}), 201
        else:
            error_details = response.text
            print("Message failed.")
            return jsonify({"error": "Failed to send OTP", "details": error_details}), 500

    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while adding the customer"}), 500
