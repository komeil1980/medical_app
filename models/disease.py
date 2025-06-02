from extensions import db
from datetime import datetime

class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ارتباط با پرونده‌های پزشکی
    records = db.relationship('MedicalRecord', backref='disease', lazy=True)
    
    def __repr__(self):
        return f'<بیماری {self.name}>'
