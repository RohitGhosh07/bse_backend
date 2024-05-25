from flask import Blueprint, jsonify, request, session

localstorage = Blueprint('localstorage', __name__)

# Initialize session_data as an empty dictionary
session_data = {}

# Route to store counter value in session and update session_data
@localstorage.route('/store_count', methods=['POST'])
def store_count():
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON data received'}), 400
    
    item_id = data.get('item_id')
    count = data.get('count')
    if item_id is None or count is None:
        return jsonify({'error': 'Missing item_id or count in JSON data'}), 400

    # Store count in session
    localStorageKey = f'item_{item_id}_count'
    session[localStorageKey] = count

    # Update session_data with the new session contents
    global session_data
    session_data = dict(session)

    # Return session data along with a success message
    return jsonify({'message': 'Count stored successfully', 'session': session_data}), 200

# Route to retrieve all counter values from local storage
@localstorage.route('/get_all_counts', methods=['GET'])
def get_all_counts():
    # Initialize dictionary to store counts for all items
    all_counts = {}
    
    # Iterate through session keys to collect counts for each item
    for key, value in session_data.items():
        # Check if the key corresponds to an item count
        if key.startswith('item_') and key.endswith('_count'):
            # Extract item ID from the key
            item_id = int(key.split('_')[1])
            # Store count for the item
            all_counts[item_id] = value

    # Check if any counts were found
    if not all_counts:
        return jsonify({'error': 'No counts found in local storage'}), 404

    # Return all counts as JSON response
    return jsonify(all_counts), 200
