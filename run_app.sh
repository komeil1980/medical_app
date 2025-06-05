#!/bin/bash

# رنگ‌ها برای خروجی زیباتر
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

echo -e "${BLUE}=== شروع اجرای برنامه مشاوره پزشکی ===${NC}"

# بررسی وجود محیط مجازی
if [ -d "venv" ]; then
    echo -e "${YELLOW}محیط مجازی قبلی یافت شد. در حال حذف...${NC}"
    rm -rf venv
    echo -e "${GREEN}محیط مجازی قبلی حذف شد.${NC}"
fi

echo -e "${YELLOW}در حال ساخت محیط مجازی جدید...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}خطا در ساخت محیط مجازی. لطفاً مطمئن شوید Python 3 نصب شده است.${NC}"
    exit 1
fi
echo -e "${GREEN}محیط مجازی با موفقیت ساخته شد.${NC}"

# فعال‌سازی محیط مجازی
echo -e "${YELLOW}در حال فعال‌سازی محیط مجازی...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}خطا در فعال‌سازی محیط مجازی.${NC}"
    exit 1
fi
echo -e "${GREEN}محیط مجازی با موفقیت فعال شد.${NC}"

# بروزرسانی pip
echo -e "${YELLOW}در حال بروزرسانی pip...${NC}"
pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo -e "${RED}خطا در بروزرسانی pip.${NC}"
    exit 1
fi
echo -e "${GREEN}pip با موفقیت بروزرسانی شد.${NC}"

# نصب نسخه‌های سازگار
echo -e "${YELLOW}در حال نصب نسخه‌های سازگار کتابخانه‌ها...${NC}"

pip install sqlalchemy==1.4.46
pip install flask==2.0.1
pip install flask-sqlalchemy==2.5.1
pip install flask-login==0.5.0
pip install flask-wtf==0.15.1
pip install email_validator==1.1.3
pip install werkzeug==2.0.1
pip install jinja2==3.0.1
pip install wtforms==2.3.3
pip install itsdangerous==2.0.1

echo -e "${GREEN}نصب کتابخانه‌ها به پایان رسید.${NC}"

# تست اتصال پایه Flask-SQLAlchemy
echo -e "${YELLOW}در حال تست اتصال به SQLAlchemy...${NC}"
python3 -c "
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
print('اتصال به SQLAlchemy موفقیت‌آمیز بود!')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}خطا در تست اتصال به SQLAlchemy.${NC}"
    exit 1
else
    echo -e "${GREEN}تست اتصال به SQLAlchemy موفقیت‌آمیز بود!${NC}"
fi

# اجرای برنامه
echo -e "${BLUE}در حال اجرای برنامه...${NC}"
echo -e "${GREEN}برنامه در آدرس http://127.0.0.1:5000 قابل دسترسی است.${NC}"
echo -e "${YELLOW}برای توقف برنامه، کلیدهای Ctrl+C را فشار دهید.${NC}"
echo -e "${BLUE}=== اطلاعات ورود ادمین ===${NC}"
echo -e "${GREEN}نام کاربری: ${YELLOW}admin${NC}"
echo -e "${GREEN}رمز عبور: ${YELLOW}admin123${NC}"

python3 app.py

# غیرفعال‌سازی محیط مجازی در پایان
deactivate