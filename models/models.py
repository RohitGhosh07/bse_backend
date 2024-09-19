from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    otp = db.Column(db.String(6))  # Column to store OTP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookmarked_items = db.Column(db.String)  # Column to store bookmarked item IDs as a comma-separated string
    session_id = db.Column(db.String(100), nullable=True)
    membership_status = db.Column(db.String(20), nullable=False, default='Guest')
