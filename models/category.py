from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.models import db

class Category(db.Model):
    __tablename__ = 'category'
        
    id = db.Column(db.Integer, primary_key=True)
    item_category_name = db.Column(db.String(255), nullable=False)
    active_slot_start = db.Column(db.Integer, nullable=False)
    active_slot_end = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Category(id={self.id}, item_category_name={self.item_category_name}, " \
               f"active_slot_start={self.active_slot_start}, active_slot_end={self.active_slot_end}, " \
               f"created_at={self.created_at})"
