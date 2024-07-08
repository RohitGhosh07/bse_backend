from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.models import db  # Import db from models.models

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, nullable=False)
    amount_loaded = db.Column(db.Float, nullable=False)
    session_id = db.Column(db.String(255), nullable=False)
    current_amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Wallet(id={self.id}, created_at={self.created_at}, customer_id={self.customer_id}, amount_loaded={self.amount_loaded}, session_id={self.session_id}, current_amount={self.current_amount})"
