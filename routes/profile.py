from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from extensions import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Detect user type
    if hasattr(current_user, 'first_name') and hasattr(current_user, 'last_name'):
        user_type = 'user'
        profile_fields = ['first_name', 'last_name', 'email', 'phone', 'gender', 'national_id']
    else:
        user_type = 'admin'
        profile_fields = ['username', 'name', 'specialty', 'email', 'phone']

    if request.method == 'POST':
        try:
            for field in profile_fields:
                value = request.form.get(field)
                print(f"[فرم] {field}: {value}")
                if value is not None and hasattr(current_user, field):
                    setattr(current_user, field, value)
            print(f"[قبل از commit] ایمیل: {getattr(current_user, 'email', None)} | شماره موبایل: {getattr(current_user, 'phone', None)}")
            db.session.add(current_user)
            db.session.commit()
            print("--- Saved profile fields ---")
            for field in profile_fields:
                if hasattr(current_user, field):
                    print(f"{field}: {getattr(current_user, field)}")
            flash('تغییرات با موفقیت ذخیره شد', 'success')
            return redirect(url_for('profile.profile'))
        except Exception as e:
            db.session.rollback()
            # مدیریت خطای یکتا بودن ایمیل یا شماره موبایل
            if 'UNIQUE constraint failed' in str(e) or 'unique constraint' in str(e).lower():
                flash('ایمیل یا شماره موبایل قبلاً ثبت شده است. لطفاً مقدار دیگری وارد کنید.', 'danger')
            else:
                flash(f'خطا در ذخیره تغییرات: {str(e)}', 'danger')
            return redirect(url_for('profile.profile'))

    return render_template('profile.html', user=current_user, user_type=user_type)


@profile_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # اعتبارسنجی‌های جدید
            if not all([current_password, new_password, confirm_password]):
                flash('لطفا تمام فیلدها را پر کنید', 'danger')
                return redirect(url_for('profile.change_password'))

            if new_password != confirm_password:
                flash('رمز جدید با تکرار آن مطابقت ندارد', 'danger')
                return redirect(url_for('profile.change_password'))

            if not current_user.verify_password(current_password):
                flash('رمز فعلی نادرست است', 'danger')
                return redirect(url_for('profile.change_password'))

            # تغییر رمز عبور
            current_user.password = new_password
            db.session.commit()
            
            # خروج اجباری و پاکسازی session
            logout_user()
            session.clear()
            
            flash('رمز عبور با موفقیت تغییر کرد. لطفا مجددا وارد شوید', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطا در تغییر رمز عبور: {str(e)}', 'danger')
            return redirect(url_for('profile.change_password'))

    return render_template('change_password.html')
