from flask import Blueprint, jsonify, request
from models.category import Category, db

category_bp = Blueprint('category_bp', __name__)

@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    category_list = [
        {
            'id': category.id,
            'item_category_name': category.item_category_name,
            'active_slot_start': category.active_slot_start,
            'active_slot_end': category.active_slot_end,
            'created_at': category.created_at
        } for category in categories
    ]
    return jsonify({"categories": category_list})


@category_bp.route("/categories", methods=["POST"])
def add_categories():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Invalid data format. Expected a list of categories."}), 400

    response_data = []

    for category_data in data:
        item_category_name = category_data.get('item_category_name')
        active_slot_start = category_data.get('active_slot_start')
        active_slot_end = category_data.get('active_slot_end')

        if not item_category_name or not active_slot_start or not active_slot_end:
            return jsonify({"error": "Incomplete data in one of the categories"}), 400

        new_category = Category(item_category_name=item_category_name, active_slot_start=active_slot_start, active_slot_end=active_slot_end)

        try:
            db.session.add(new_category)
            db.session.commit()
            response_data.append({
                'id': new_category.id,
                'item_category_name': new_category.item_category_name,
                'active_slot_start': new_category.active_slot_start,
                'active_slot_end': new_category.active_slot_end,
                'created_at': new_category.created_at
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "An error occurred while adding the categories"}), 500

    return jsonify({"message": "Categories added successfully", "categories": response_data}), 201

