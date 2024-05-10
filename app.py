from flask import Flask
from models.models import db
from routes.customer_routes import customer_bp
from routes.otp_routes import otp_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/BSE'
db.init_app(app)

# Register blueprints
app.register_blueprint(customer_bp)
app.register_blueprint(otp_bp)

if __name__ == "__main__":
    app.run(debug=True)
