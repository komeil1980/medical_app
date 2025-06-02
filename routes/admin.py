from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.admin import Admin
from models.user import User
from models.disease import Disease
from models.medical_record import MedicalRecord, MedicalFile, Payment
from models.doctor import doctor_records, Opinion
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# تزئین‌کننده برای بررسی دسترسی ادمین
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.__class__.__name__ != 'Admin' or not current_user.is_admin():
            flash('شما دسترسی به این بخش را ندارید!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# تزئین‌کننده برای بررسی دسترسی ادمین دکتر
def doctor_admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.__class__.__name__ != 'Admin' or not (current_user.is_doctor_admin() or current_user.is_admin()):
            flash('شما دسترسی به این بخش را ندارید!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# تزئین‌کننده برای بررسی دسترسی پزشک
def doctor_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.__class__.__name__ != 'Admin' or not (current_user.is_doctor() or current_user.is_doctor_admin() or current_user.is_admin()):
            flash('شما دسترسی به این بخش را ندارید!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# داشبورد ادمین کل
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    users_count = User.query.count()
    doctors_count = Admin.query.filter_by(role='doctor').count()
    records_count = MedicalRecord.query.count()
    payments_sum = db.session.query(func.sum(Payment.amount)).filter_by(status='موفق').scalar() or 0
    
    recent_records = MedicalRecord.query.order_by(MedicalRecord.created_at.desc()).limit(10).all()
    recent_payments = Payment.query.filter_by(status='موفق').order_by(Payment.payment_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           users_count=users_count, 
                           doctors_count=doctors_count,
                           records_count=records_count,
                           payments_sum=payments_sum,
                           recent_records=recent_records,
                           recent_payments=recent_payments)

# داشبورد ادمین دکتر
@admin_bp.route('/doctor-admin-dashboard')
@doctor_admin_required
def doctor_admin_dashboard():
    # پرونده‌های جدیدی که هنوز بررسی نشده‌اند
    new_records = MedicalRecord.query.filter(
        MedicalRecord.status.in_(['در حال بررسی']),
        MedicalRecord.assigned_doctor_admin_id.is_(None)
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    # پرونده‌های در حال بررسی توسط این ادمین دکتر
    my_records = MedicalRecord.query.filter_by(
        assigned_doctor_admin_id=current_user.id
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    # پرونده‌های منتظر نظر نهایی
    pending_final_records = MedicalRecord.query.filter(
        MedicalRecord.assigned_doctor_admin_id == current_user.id,
        MedicalRecord.status == 'در انتظار نظر نهایی'
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    return render_template('admin/doctor_admin_dashboard.html',
                           new_records=new_records,
                           my_records=my_records,
                           pending_final_records=pending_final_records)

# داشبورد پزشک
@admin_bp.route('/doctor-dashboard')
@doctor_required
def doctor_dashboard():
    # پرونده‌های تخصیص داده شده به پزشک که هنوز بررسی نشده‌اند
    new_assigned_records = MedicalRecord.query.join(
        doctor_records,
        (doctor_records.c.record_id == MedicalRecord.id) & 
        (doctor_records.c.doctor_id == current_user.id)
    ).filter(
        ~MedicalRecord.opinions.any(Opinion.doctor_id == current_user.id)
    ).all()
    
    # پرونده‌هایی که پزشک قبلاً بررسی کرده است
    reviewed_records = MedicalRecord.query.join(Opinion).filter(
        Opinion.doctor_id == current_user.id
    ).all()
    
    return render_template('admin/doctor_dashboard.html',
                           new_assigned_records=new_assigned_records,
                           reviewed_records=reviewed_records)

# مدیریت کاربران
@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# مدیریت پزشکان و ادمین‌ها
@admin_bp.route('/staff')
@admin_required
def manage_staff():
    staff = Admin.query.all()
    return render_template('admin/staff.html', staff=staff)

# افزودن پزشک/ادمین جدید
@admin_bp.route('/staff/add', methods=['GET', 'POST'])
@admin_required
def add_staff():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        name = request.form.get('name')
        specialty = request.form.get('specialty')
        
        # بررسی تکراری نبودن نام کاربری
        if Admin.query.filter_by(username=username).first():
            flash('این نام کاربری قبلاً ثبت شده است!', 'danger')
            return redirect(url_for('admin.add_staff'))
        
        # ایجاد ادمین جدید
        new_staff = Admin(
            username=username,
            password=password,
            role=role,
            name=name,
            specialty=specialty
        )
        
        db.session.add(new_staff)
        db.session.commit()
        
        flash('کاربر جدید با موفقیت اضافه شد!', 'success')
        return redirect(url_for('admin.manage_staff'))
        
    return render_template('admin/add_staff.html')

# مدیریت بیماری‌ها
@admin_bp.route('/diseases')
@admin_required
def manage_diseases():
    diseases = Disease.query.all()
    return render_template('admin/diseases.html', diseases=diseases)

# افزودن بیماری جدید
@admin_bp.route('/diseases/add', methods=['GET', 'POST'])
@admin_required
def add_disease():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        is_active = 'is_active' in request.form
        
        # ایجاد بیماری جدید
        new_disease = Disease(
            name=name,
            category=category,
            description=description,
            is_active=is_active
        )
        
        db.session.add(new_disease)
        db.session.commit()
        
        flash('بیماری جدید با موفقیت اضافه شد!', 'success')
        return redirect(url_for('admin.manage_diseases'))
        
    return render_template('admin/add_disease.html')

# بررسی پرونده توسط ادمین دکتر
@admin_bp.route('/record/review/<int:record_id>', methods=['GET', 'POST'])
@doctor_admin_required
def review_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'assign':
            # تخصیص پرونده به خود
            record.assigned_doctor_admin_id = current_user.id
            record.status = 'در حال بررسی توسط ادمین دکتر'
            db.session.commit()
            flash('پرونده به شما تخصیص داده شد!', 'success')
        
        elif action == 'assign_doctors':
            # تخصیص پرونده به پزشکان
            doctor_ids = request.form.getlist('doctor_ids')
            
            if not doctor_ids:
                flash('لطفاً حداقل یک پزشک انتخاب کنید!', 'danger')
                return redirect(url_for('admin.review_record', record_id=record_id))
            
            for doctor_id in doctor_ids:
                doctor = Admin.query.get(doctor_id)
                if doctor and (doctor.role == 'doctor' or doctor.role == 'doctor_admin'):
                    record.assigned_doctors.append(doctor)
            
            record.status = 'ارجاع شده به پزشک'
            db.session.commit()
            flash('پرونده به پزشکان انتخابی ارجاع داده شد!', 'success')
        
        elif action == 'final_verdict':
            # ثبت نظر نهایی
            final_verdict = request.form.get('final_verdict')
            record.final_verdict = final_verdict
            record.final_verdict_date = datetime.utcnow()
            record.status = 'نظر نهایی اعلام شده'
            db.session.commit()
            flash('نظر نهایی با موفقیت ثبت شد!', 'success')
        
        return redirect(url_for('admin.doctor_admin_dashboard'))
    
    # لیست پزشکان برای تخصیص
    doctors = Admin.query.filter(Admin.role.in_(['doctor', 'doctor_admin']), Admin.is_active == True).all()
    
    return render_template('admin/review_record.html', record=record, doctors=doctors)

# ثبت نظر پزشک
@admin_bp.route('/record/opinion/<int:record_id>', methods=['GET', 'POST'])
@doctor_required
def submit_opinion(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    
    # بررسی اینکه آیا پرونده به این پزشک تخصیص داده شده است
    if current_user not in record.assigned_doctors and current_user.id != record.assigned_doctor_admin_id:
        flash('این پرونده به شما تخصیص داده نشده است!', 'danger')
        return redirect(url_for('admin.doctor_dashboard'))
    
    if request.method == 'POST':
        opinion_text = request.form.get('opinion_text')
        
        # بررسی اینکه آیا قبلاً نظری ثبت شده است
        existing_opinion = Opinion.query.filter_by(doctor_id=current_user.id, record_id=record_id).first()
        
        if existing_opinion:
            # به‌روزرسانی نظر موجود
            existing_opinion.text = opinion_text
            flash('نظر شما با موفقیت به‌روزرسانی شد!', 'success')
        else:
            # ایجاد نظر جدید
            new_opinion = Opinion(
                doctor_id=current_user.id,
                record_id=record_id,
                text=opinion_text
            )
            db.session.add(new_opinion)
            flash('نظر شما با موفقیت ثبت شد!', 'success')
        
        # بررسی اینکه آیا همه پزشکان نظر داده‌اند
        all_doctors_opined = all(
            Opinion.query.filter_by(doctor_id=doctor.id, record_id=record_id).first() 
            for doctor in record.assigned_doctors
        )
        
        if all_doctors_opined:
            record.status = 'در انتظار نظر نهایی'
        
        db.session.commit()
        return redirect(url_for('admin.doctor_dashboard'))
    
    # بررسی نظر قبلی
    existing_opinion = Opinion.query.filter_by(doctor_id=current_user.id, record_id=record_id).first()
    
    return render_template('admin/submit_opinion.html', record=record, existing_opinion=existing_opinion)
