# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.models import db  # Import db from models.models



class PriceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    time_of_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=False)
    market_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"PriceLog(id={self.id}, item_id={self.item_id}, time_of_update={self.time_of_update}, price={self.price}, market_date={self.market_date})"
