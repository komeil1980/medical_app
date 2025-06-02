from flask import Flask, render_template, flash
from config import Config
from extensions import db, login_manager
import os

# ایجاد پوشه‌های مورد نیاز
os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'uploads'), exist_ok=True)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # اطمینان از وجود پوشه instance
    os.makedirs(app.instance_path, exist_ok=True)
    
    # مقداردهی آبجکت‌ها
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'لطفا وارد حساب کاربری خود شوید'
    
    with app.app_context():
        # ثبت بلوپرینت‌ها
        from routes.main import main_bp
        from routes.auth import auth_bp
        from routes.admin import admin_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # ایجاد جداول
        db.create_all()
        
        # واردات مدل‌ها
        from models.admin import Admin
        from models.disease import Disease
        
        # ایجاد ادمین اصلی اگر وجود نداشته باشد
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin', password='admin123', role='superadmin')
            db.session.add(admin)
            db.session.commit()
            
        # ایجاد بیماری‌های پیش‌فرض
        if not Disease.query.first():
            diseases = [
                Disease(name='سرطان پستان', category='سرطان', is_active=True),
                Disease(name='سرطان ریه', category='سرطان', is_active=True),
                Disease(name='سرطان پوست', category='سرطان', is_active=True)
            ]
            db.session.add_all(diseases)
            db.session.commit()
        
        @app.errorhandler(404)
        def page_not_found(e):
            return render_template('error.html', error_code=404, message='صفحه مورد نظر یافت نشد'), 404
        
        @app.errorhandler(500)
        def internal_server_error(e):
            return render_template('error.html', error_code=500, message='خطای داخلی سرور'), 500
            
        # افزودن فیلترهای سفارشی به Jinja
        @app.template_filter('nl2br')
        def nl2br_filter(s):
            if s:
                return s.replace('\n', '<br>')
            return s
            
        return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)