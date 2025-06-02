from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='doctor')  # superadmin, doctor_admin, doctor
    name = db.Column(db.String(100), nullable=True)
    specialty = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ادمین {self.username}>'
    
    @property
    def password(self):
        raise AttributeError('رمز عبور قابل خواندن نیست!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'superadmin'
    
    def is_doctor_admin(self):
        return self.role == 'doctor_admin'
    
    def is_doctor(self):
        return self.role == 'doctor' or self.is_doctor_admin()
        
    def get_id(self):
        # بازنویسی متد get_id برای تمایز بین کاربران معمولی و ادمین‌ها
        return f"admin_{self.id}"