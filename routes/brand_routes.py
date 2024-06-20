from flask import Blueprint, request, jsonify
from models.models import db
from models.brand import Brand

brand_bp = Blueprint('brand_bp', __name__)

@brand_bp.route('/brands', methods=['POST'])
def create_brands():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid JSON data format. Expected an array of brands.'}), 400

    response_data = []

    for brand_data in data:
        name = brand_data.get('name')
        image = brand_data.get('image')

        if not name or not image:
            return jsonify({'error': 'Name and image are required for each brand.'}), 400

        new_brand = Brand(name=name, image=image)

        try:
            db.session.add(new_brand)
            db.session.commit()
            response_data.append({
                'id': new_brand.id,
                'name': new_brand.name,
                'image': new_brand.image,
                'created_at': new_brand.created_at
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'An error occurred while adding a brand: {str(e)}'}), 500

    return jsonify({
        'message': 'Brands added successfully',
        'brands': response_data
    }), 201

@brand_bp.route('/brands', methods=['GET'])
def get_brands():
    brands = Brand.query.all()
    results = [
        {
            'id': brand.id,
            'name': brand.name,
            'image': brand.image,
            'created_at': brand.created_at
        } for brand in brands]

    return jsonify(results), 200

@brand_bp.route('/brands/<int:id>', methods=['GET'])
def get_brand(id):
    brand = Brand.query.get_or_404(id)
    return jsonify({
        'id': brand.id,
        'name': brand.name,
        'image': brand.image,
        'created_at': brand.created_at
    }), 200
