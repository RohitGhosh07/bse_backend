from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models.models import db  # Import db from models.models
from routes.customer_routes import customer_bp
from routes.otp_routes import otp_bp
from routes.category_routes import category_bp
from routes.items_routes import items_bp
from routes.pricelogs_routes import price_logs_bp
from routes.order_log_routes import order_logs_bp
from routes.localstorage import localstorage
from routes.bookmark_routes import bookmark_bp
from routes.brand_routes import brand_bp
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = '1234567890'  # Set the secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/BSE'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'  # Specify the CORS headers

db.init_app(app)
migrate = Migrate(app, db)
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
app.register_blueprint(price_logs_bp)
app.register_blueprint(order_logs_bp)
app.register_blueprint(localstorage)
app.register_blueprint(bookmark_bp)
app.register_blueprint(brand_bp)

if __name__ == "__main__":
    app.run(debug=True)
