from extensions import db
from datetime import datetime

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'), nullable=False)
    chief_complaint = db.Column(db.Text, nullable=False)
    history_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='جدید', nullable=False)
    assigned_doctor_admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    final_verdict = db.Column(db.Text, nullable=True)
    final_verdict_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ارتباط با ادمین دکتر
    doctor_admin = db.relationship('Admin', foreign_keys=[assigned_doctor_admin_id])
    
    # ارتباط با پزشکان تخصیص داده شده (many-to-many)
    assigned_doctors = db.relationship('Admin', 
                                      secondary='doctor_records',
                                      lazy='subquery',
                                      backref=db.backref('assigned_records', lazy=True))
    
    # ارتباط با نظرات پزشکان
    opinions = db.relationship('Opinion', backref='record', lazy=True)
    
    # ارتباط با فایل‌های پزشکی
    files = db.relationship('MedicalFile', backref='record', lazy=True)
    
    # ارتباط با تراکنش‌های مالی
    payments = db.relationship('Payment', backref='record', lazy=True)
    
    def __repr__(self):
        return f'<پرونده {self.id} - بیمار {self.user_id}>'

class MedicalFile(db.Model):
    __tablename__ = 'medical_files'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<فایل {self.file_name} - پرونده {self.record_id}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='در انتظار', nullable=False)
    payment_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<پرداخت {self.id} - پرونده {self.record_id}>'
