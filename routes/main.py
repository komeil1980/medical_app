from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models.disease import Disease
from models.medical_record import MedicalRecord, MedicalFile, Payment
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# صفحه اصلی
@main_bp.route('/')
def index():
    return render_template('index.html')

# داشبورد کاربر
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.__class__.__name__ != 'User':  # اگر ادمین است
        if current_user.role == 'superadmin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'doctor_admin':
            return redirect(url_for('admin.doctor_admin_dashboard'))
        else:
            return redirect(url_for('admin.doctor_dashboard'))
    
    # نمایش پرونده‌های کاربر
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(MedicalRecord.created_at.desc()).all()
    return render_template('dashboard.html', records=records)

# ایجاد پرونده پزشکی جدید
@main_bp.route('/record/create', methods=['GET', 'POST'])
@login_required
def create_record():
    if current_user.__class__.__name__ != 'User':  # اگر ادمین است
        flash('فقط بیماران می‌توانند پرونده ایجاد کنند!', 'danger')
        return redirect(url_for('main.dashboard'))
    
    diseases = Disease.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        # کپچای ریاضی
        captcha_answer = request.form.get('captcha_answer')
        captcha_correct = request.form.get('captcha_correct')
        if not captcha_answer or not captcha_correct or captcha_answer.strip() != captcha_correct.strip():
            flash('پاسخ کپچا صحیح نیست. لطفاً دوباره تلاش کنید.', 'danger')
            return render_template('record/create.html', diseases=diseases)

        disease_id = request.form.get('disease_id')
        chief_complaint = request.form.get('chief_complaint')
        history_notes = request.form.get('history_notes')
        
        # ایجاد پرونده جدید
        record = MedicalRecord(
            user_id=current_user.id,
            disease_id=disease_id,
            chief_complaint=chief_complaint,
            history_notes=history_notes,
            status='در انتظار پرداخت'
        )
        db.session.add(record)
        db.session.commit()
        
        # آپلود فایل‌ها
        files = request.files.getlist('files')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # ایجاد رکورد فایل
                medical_file = MedicalFile(
                    record_id=record.id,
                    file_name=filename,
                    file_path=unique_filename,
                    file_type=file.content_type,
                    file_size=os.path.getsize(file_path),
                    description=request.form.get(f'description_{file.filename}', '')
                )
                db.session.add(medical_file)
        
        # ایجاد رکورد پرداخت
        payment = Payment(
            record_id=record.id,
            amount=500000,  # مبلغ ثابت (در سیستم واقعی می‌تواند متغیر باشد)
            status='در انتظار'
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('پرونده شما با موفقیت ثبت شد. لطفاً نسبت به پرداخت هزینه مشاوره اقدام کنید.', 'success')
        return redirect(url_for('main.payment', record_id=record.id))
        
    return render_template('record/create.html', diseases=diseases)

# صفحه پرداخت
@main_bp.route('/payment/<int:record_id>')
@login_required
def payment(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    
    # بررسی مالکیت پرونده
    if record.user_id != current_user.id and current_user.__class__.__name__ == 'User':
        flash('شما مجاز به دسترسی به این پرونده نیستید!', 'danger')
        return redirect(url_for('main.dashboard'))
    
    payment = Payment.query.filter_by(record_id=record_id).first_or_404()
    
    # در یک سیستم واقعی، در اینجا به درگاه پرداخت هدایت می‌شود
    # برای سادگی، ما فرض می‌کنیم پرداخت انجام شده است
    payment.status = 'موفق'
    payment.payment_date = datetime.utcnow()
    payment.transaction_id = f"SIMULATED_{uuid.uuid4().hex[:8]}"
    
    record.status = 'در حال بررسی'
    
    db.session.commit()
    
    flash('پرداخت با موفقیت انجام شد. پرونده شما در صف بررسی قرار گرفت.', 'success')
    return redirect(url_for('main.view_record', record_id=record_id))

# نمایش پرونده
@main_bp.route('/record/<int:record_id>')
@login_required
def view_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    
    # بررسی دسترسی
    if record.user_id != current_user.id and current_user.__class__.__name__ == 'User':
        flash('شما مجاز به دسترسی به این پرونده نیستید!', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('record/view.html', record=record)