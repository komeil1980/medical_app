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
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ادمین {self.username}>'
    
    @property
    def password(self):
        raise AttributeError('رمز عبور قابل خواندن نیست!')
    
    @password.setter
    def password(self, password):
        if not isinstance(password, str):
            password = str(password)
        # اضافه کردن بررسی طول رمز عبور
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters')
        print(f"Generating hash for password: {password}")
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def verify_password(self, password):
        if not isinstance(password, str):
            password = str(password)
        print(f"Verifying password: {password} against hash: {self.password_hash}")
        # اضافه کردن لاگ برای دیباگ
        print(f"Password: {password}")
        print(f"Stored hash: {self.password_hash}")
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