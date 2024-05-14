from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.models import db



class OrderLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_placed_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    item_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.String(20), nullable=False)
