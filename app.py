from flask import Flask, render_template
from models.models import db
from routes.customer_routes import customer_bp
from routes.otp_routes import otp_bp
from routes.category_routes import category_bp
from routes.items_routes import items_bp
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/BSE'
app.config['CORS_HEADERS'] = 'Content-Type'  # Specify the CORS headers
db.init_app(app)
CORS(app)  # Enable CORS for all routes

# Create all tables
with app.app_context():
    db.create_all()
    
@app.route("/")
def home():
    return render_template("index.html", message="Api is Running for BSE APP")

# Register blueprints
app.register_blueprint(customer_bp)
app.register_blueprint(otp_bp)
app.register_blueprint(category_bp)
app.register_blueprint(items_bp)

if __name__ == "__main__":
    app.run(debug=True)
