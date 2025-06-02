from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
from models.admin import Admin
from datetime import datetime, timedelta
import random

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        # بررسی تکراری نبودن شماره موبایل
        user = User.query.filter_by(phone=phone).first()
        if user:
            flash('این شماره موبایل قبلاً ثبت شده است!', 'danger')
            return redirect(url_for('auth.register'))
        
        # بررسی ایمیل تکراری
        if email and User.query.filter_by(email=email).first():
            flash('این ایمیل قبلاً ثبت شده است!', 'danger')
            return redirect(url_for('auth.register'))
        
        # ایجاد کاربر جدید
        new_user = User(
            phone=phone,
            email=email,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            gender=request.form.get('gender')
        )
        
        # تولید OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        new_user.otp_code = otp
        new_user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        db.session.add(new_user)
        db.session.commit()
        
        # برای سادگی، OTP را نمایش می‌دهیم (در سیستم واقعی باید پیامک شود)
        flash(f'کد یکبار مصرف (OTP) شما: {otp}', 'info')
        
        # ذخیره تلفن در session برای صفحه ورود
        session['phone'] = phone
        
        return redirect(url_for('auth.verify_otp'))
        
    return render_template('auth/register.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'phone' not in session:
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        phone = session['phone']
        otp = request.form.get('otp')
        
        user = User.query.filter_by(phone=phone).first()
        if not user:
            flash('کاربری با این شماره تلفن یافت نشد!', 'danger')
            return redirect(url_for('auth.register'))
        
        # بررسی OTP
        if user.otp_code == otp and user.otp_expiry > datetime.utcnow():
            # پاک کردن OTP پس از استفاده
            user.otp_code = None
            user.otp_expiry = None
            db.session.commit()
            
            login_user(user)
            flash('شما با موفقیت وارد شدید!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('کد OTP نامعتبر یا منقضی شده است!', 'danger')
    
    return render_template('auth/verify_otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        phone = request.form.get('phone')
        user = User.query.filter_by(phone=phone).first()
        
        if not user:
            # کاربر وجود ندارد، بنابراین ثبت‌نام می‌کنیم
            return redirect(url_for('auth.register', phone=phone))
        
        # تولید OTP جدید
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        # برای سادگی، OTP را نمایش می‌دهیم (در سیستم واقعی باید پیامک شود)
        flash(f'کد یکبار مصرف (OTP) شما: {otp}', 'info')
        
        # ذخیره تلفن در session برای صفحه ورود
        session['phone'] = phone
        
        return redirect(url_for('auth.verify_otp'))
        
    return render_template('auth/login.html')

@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if not admin or not admin.verify_password(password):
            flash('نام کاربری یا رمز عبور اشتباه است!', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if not admin.is_active:
            flash('حساب کاربری شما غیرفعال شده است!', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        login_user(admin)
        flash('شما با موفقیت وارد شدید!', 'success')
        
        # هدایت به داشبورد مناسب بر اساس نقش
        if admin.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif admin.is_doctor_admin():
            return redirect(url_for('admin.doctor_admin_dashboard'))
        else:
            return redirect(url_for('admin.doctor_dashboard'))
    
    return render_template('auth/admin_login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('با موفقیت خارج شدید!', 'success')
    return redirect(url_for('main.index'))
