from flask import Blueprint, jsonify, request
from models.models import db, Customer
import vonage
import random
from datetime import datetime

customer_bp = Blueprint('customer_bp', __name__)

# Initialize Vonage client
client = vonage.Client(key="474478d6", secret="kAp2EA8BjHONaYly")
sms = vonage.Sms(client)

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
        # otp = ''.join(random.choices('0123456789', k=6))

        # # Save OTP to the new customer object
        otp = "123456"
        new_customer.otp = otp

        # Print the OTP value for debugging
        print("Generated OTP:", otp)
        
        # Add the new customer to the session
        db.session.add(new_customer)
        
        # Commit the session to save the new customer and OTP to the database
        db.session.commit()

        # Send OTP to the provided phone number
        responseData = sms.send_message(
            {
                "from": "Vonage",
                "to": f"91{phone}",
                "text": f"Your OTP for login in BSE is: {otp}"
            }
        )

        if responseData["messages"][0]["status"] == "0":
            print("Message sent successfully.")
        else:
            print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        # Return the ID of the newly added customer along with the success response
        return jsonify({"message": "OTP sent successfully", "id": new_customer.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the customer"}), 500
