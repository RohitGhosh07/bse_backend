from datetime import datetime, time
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



# Route to add a new customer
@customer_bp.route("/customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400
    
    name = data.get('name', None)  # Set name to None if not provided

    # Check if 'membership_status' is provided in the request
    membership_status = data.get('membership_status', 'Guest')  # Default to 'Guest' if not provided
    
    new_customer = Customer(
        name=name, 
        phone=phone, 
        membership_status=membership_status
    )
    
    try:
        # Generate a random 6-digit OTP
        # otp = ''.join(random.choices('0123456789', k=6))
        otp = '000000'
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

        if response.status_code == 200:
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
    
    
# Route to get today's customers
@customer_bp.route("/todaycustomers", methods=["GET"], endpoint="get_today_customers")
def get_today_customers():
    # Get today's date
    today_start = datetime.combine(datetime.today(), time.min)
    today_end = datetime.combine(datetime.today(), time.max)
    
    # Query customers created today
    customers = Customer.query.filter(Customer.created_at >= today_start, Customer.created_at <= today_end).order_by(Customer.created_at.desc()).all()
    
    # Convert query results to list of dictionaries
    customer_list = [
        {
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'otp': customer.otp,
            'membership_status': customer.membership_status,
            'created_at': customer.created_at.isoformat(),  # Convert datetime to ISO format string
            'session_id': customer.session_id
        }
        for customer in customers
    ]
    
    return jsonify({"customers": customer_list})

# Route to get all customers
@customer_bp.route("/customers", methods=["GET"])
def get_all_customers():
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    customer_list = [
        {
        'id': customer.id,
        'name': customer.name, 
        'phone': customer.phone, 
        'otp': customer.otp, 
        'membership_status': customer.membership_status,
        'created_at': customer.created_at.isoformat()
        } 
        for customer in customers
    ]
    return jsonify({"customers": customer_list})

# update api to update the customer name
@customer_bp.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer_name(customer_id):
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    try:
        # Query the customer by ID
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Update the customer's name
        customer.name = name
        
        # Commit the session to save the changes
        db.session.commit()
        
        return jsonify({"message": "Customer name updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while updating the customer name"}), 500
