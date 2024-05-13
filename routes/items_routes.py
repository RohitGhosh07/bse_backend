from flask import Blueprint, jsonify, request
from models.items import Item, db

items_bp = Blueprint('items_bp', __name__)


@items_bp.route("/items", methods=["GET"])
def get_items():
    item_category_id = request.args.get('item_category_id')

    if item_category_id is not None:
        items = Item.query.filter_by(item_category_id=item_category_id).all()
    else:
        items = Item.query.all()

    item_list = [
        {
            'item_id': item.item_id,
            'item_name': item.item_name,
            'inventory': item.inventory,
            'item_category_id': item.item_category_id,
            'upper_circuit': item.upper_circuit,
            'lower_circuit': item.lower_circuit,
            'base_price': item.base_price,
            'subscription_id': item.subscription_id,
            'active_slot': item.active_slot,
            'created_at': item.created_at
        } for item in items
    ]
    return jsonify({"items": item_list})


@items_bp.route("/items", methods=["POST"])
def add_items():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Invalid JSON data format. Expected an array of items."}), 400

    response_data = []

    for item_data in data:
        item_name = item_data.get('item_name')
        inventory = item_data.get('inventory')
        item_category_id = item_data.get('item_category_id')
        upper_circuit = item_data.get('upper_circuit')
        lower_circuit = item_data.get('lower_circuit')
        base_price = item_data.get('base_price')
        subscription_id = item_data.get('subscription_id')
        active_slot = item_data.get('active_slot')

        if not item_name or not inventory or not item_category_id or not base_price or not active_slot:
            return jsonify({"error": "Incomplete data in one of the items."}), 400

        new_item = Item(item_name=item_name, inventory=inventory, item_category_id=item_category_id,
                        upper_circuit=upper_circuit, lower_circuit=lower_circuit, base_price=base_price,
                        subscription_id=subscription_id, active_slot=active_slot)

        try:
            db.session.add(new_item)
            db.session.commit()
            response_data.append({
                'item_id': new_item.item_id,
                'item_name': new_item.item_name,
                'inventory': new_item.inventory,
                'item_category_id': new_item.item_category_id,
                'upper_circuit': new_item.upper_circuit,
                'lower_circuit': new_item.lower_circuit,
                'base_price': new_item.base_price,
                'subscription_id': new_item.subscription_id,
                'active_slot': new_item.active_slot,
                'created_at': new_item.created_at
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred while adding an item: {str(e)}"}), 500

    return jsonify({"message": "Items added successfully", "items": response_data}), 201
