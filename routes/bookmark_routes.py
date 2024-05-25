from flask import Blueprint, jsonify, request
from models.models import db, Customer

# Create a blueprint for the bookmark routes
bookmark_bp = Blueprint('bookmark', __name__)

@bookmark_bp.route('/bookmarks', methods=['POST'])
def add_bookmark():
    try:
        data = request.json
        print(f"Received data: {data}")
        
        phone = data.get('phone')
        new_bookmarked_items = data.get('bookmarked_items')

        if not phone or not new_bookmarked_items:
            print("Missing phone number or bookmarked items")
            return jsonify({'error': 'Phone number and bookmarked items are required'}), 400

        # Find all customers by phone number
        customers = Customer.query.filter_by(phone=phone).all()
        print(f"Customers found: {customers}")

        if not customers:
            print("Customers not found")
            return jsonify({'error': 'Customers not found'}), 404

        # Convert the new bookmarked items to a set of integers
        new_bookmarked_items_set = set(map(int, new_bookmarked_items))

        for customer in customers:
            # Retrieve and parse the existing bookmarked items
            if customer.bookmarked_items:
                existing_bookmarked_items_set = set(map(int, customer.bookmarked_items.split(',')))
            else:
                existing_bookmarked_items_set = set()

            # Merge the existing and new bookmarked items
            merged_bookmarked_items_set = existing_bookmarked_items_set.union(new_bookmarked_items_set)

            # Convert the merged set back to a comma-separated string
            customer.bookmarked_items = ','.join(map(str, merged_bookmarked_items_set))
            print(f"Updated customer {customer.id} with bookmarked items: {customer.bookmarked_items}")

        db.session.commit()
        print("Bookmarks updated successfully for all customers with the same phone number")

        return jsonify({'message': 'Bookmarks added successfully for all customers with the same phone number'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@bookmark_bp.route('/bookmarks', methods=['DELETE'])
def delete_bookmark():
    try:
        data = request.json
        print(f"Received data: {data}")

        phone = data.get('phone')
        items_to_delete = data.get('items_to_delete')

        if not phone or not items_to_delete:
            print("Missing phone number or items to delete")
            return jsonify({'error': 'Phone number and items to delete are required'}), 400

        # Find all customers with the given phone number
        customers = Customer.query.filter_by(phone=phone).all()
        print(f"Customers found: {customers}")

        if not customers:
            print("Customers not found")
            return jsonify({'error': 'Customers not found'}), 404

        for customer in customers:
            # Retrieve and parse the existing bookmarked items for each customer
            if customer.bookmarked_items:
                existing_bookmarked_items_set = set(map(int, customer.bookmarked_items.split(',')))
            else:
                print(f"No bookmarked items found for customer {customer.id}")
                continue  # Skip to the next customer if no bookmarks found

            # Convert the items to delete to a set of integers
            items_to_delete_set = set(map(int, items_to_delete))

            # Remove the specified items from the existing bookmarked items
            updated_bookmarked_items_set = existing_bookmarked_items_set - items_to_delete_set

            # Convert the updated set back to a comma-separated string
            customer.bookmarked_items = ','.join(map(str, updated_bookmarked_items_set))
            print(f"Updated customer {customer.id} with bookmarked items: {customer.bookmarked_items}")

        db.session.commit()
        print("Bookmarks deleted successfully")

        return jsonify({'message': 'Bookmarks deleted successfully'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@bookmark_bp.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    try:
        phone = request.args.get('phone')

        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400

        # Find the customer by phone number
        customer = Customer.query.filter_by(phone=phone).first()

        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        # Convert the comma-separated string to a list of integers
        bookmarked_items = list(map(int, customer.bookmarked_items.split(','))) if customer.bookmarked_items else []

        return jsonify({'bookmarked_items': bookmarked_items}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
