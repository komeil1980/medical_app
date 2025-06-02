from extensions import db
from datetime import datetime

# جدول ارتباطی بین دکترها و پرونده‌های پزشکی (many-to-many)
doctor_records = db.Table('doctor_records',
    db.Column('doctor_id', db.Integer, db.ForeignKey('admins.id'), primary_key=True),
    db.Column('record_id', db.Integer, db.ForeignKey('medical_records.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)

class Opinion(db.Model):
    __tablename__ = 'opinions'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ارتباط با دکتر
    doctor = db.relationship('Admin', backref='opinions')
    
    def __repr__(self):
        return f'<نظر دکتر {self.doctor_id} برای پرونده {self.record_id}>'
