from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.models import db  # Import db from models.models

class Item(db.Model):
    __tablename__ = 'items table'
        
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    inventory = db.Column(db.Integer, nullable=False)
    item_category_id = db.Column(db.Integer, nullable=False)
    upper_circuit = db.Column(db.Float)
    lower_circuit = db.Column(db.Float)
    base_price = db.Column(db.Float, nullable=False)
    subscription_id = db.Column(db.Integer)
    active_slot = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Item(item_id={self.item_id}, item_name={self.item_name}, inventory={self.inventory}, item_category_id={self.item_category_id}, " \
               f"upper_circuit={self.upper_circuit}, lower_circuit={self.lower_circuit}, base_price={self.base_price}, " \
               f"subscription_id={self.subscription_id}, active_slot={self.active_slot}, created_at={self.created_at})"
