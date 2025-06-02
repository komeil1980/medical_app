#!/usr/bin/env python3
from app import app
from extensions import db
from models.admin import Admin
from models.disease import Disease

with app.app_context():
    print("شروع ایجاد پایگاه داده...")
    
    # حذف و ایجاد مجدد جداول
    db.drop_all()
    db.create_all()
    
    print("جداول ایجاد شدند...")
    
    # ایجاد ادمین اصلی
    admin = Admin(username='admin', password='admin123', role='superadmin')
    db.session.add(admin)
    
    # ایجاد ادمین دکتر
    doctor_admin = Admin(username='doctor_admin', password='doctor123', role='doctor_admin')
    db.session.add(doctor_admin)
    
    # ایجاد پزشک معمولی
    doctor = Admin(username='doctor', password='doctor123', role='doctor', name='دکتر محمد رضایی', specialty='انکولوژی')
    db.session.add(doctor)
    
    # ایجاد بیماری‌های پیش‌فرض
    diseases = [
        Disease(name='سرطان پستان', category='سرطان', is_active=True),
        Disease(name='سرطان ریه', category='سرطان', is_active=True),
        Disease(name='سرطان پوست', category='سرطان', is_active=True),
        Disease(name='سرطان روده', category='سرطان', is_active=True),
        Disease(name='سرطان پروستات', category='سرطان', is_active=True),
    ]
    db.session.add_all(diseases)
    
    db.session.commit()
    print("دیتابیس با موفقیت ایجاد و مقداردهی اولیه شد!")