from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

@login_manager.user_loader
def load_user(user_id):
    from models.admin import Admin
    # بررسی اینکه آیا کاربر ادمین است یا خیر
    if user_id.startswith('admin_'):
        real_id = int(user_id.split('_')[1])
        return Admin.query.get(real_id)
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    national_id = db.Column(db.String(20), nullable=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ارتباط با پرونده‌های پزشکی
    records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<کاربر {self.phone}>'
    
    def generate_otp(self):
        import random
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp_code = otp
        self.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        return otp
    
    def verify_otp(self, otp):
        if self.otp_code == otp and datetime.utcnow() <= self.otp_expiry:
            self.otp_code = None
            self.otp_expiry = None
            return True
        return False
        
    def get_id(self):
        # بازنویسی متد get_id برای برگرداندن مقدار ساده (بدون پیشوند)
        return str(self.id)