from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.models import db

class Brand(db.Model):
    __tablename__ = 'brand'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Brand(id={self.id}, name={self.name}, image={self.image}, created_at={self.created_at})"
