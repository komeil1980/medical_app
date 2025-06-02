// فایل اسکریپت اصلی
document.addEventListener('DOMContentLoaded', function() {
    // اجرای کد پس از بارگذاری صفحه
    console.log('صفحه با موفقیت بارگذاری شد!');
    
    // بستن هشدارها با انیمیشن
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert) {
                let fadeEffect = setInterval(function() {
                    if (!alert.style.opacity) {
                        alert.style.opacity = 1;
                    }
                    if (alert.style.opacity > 0) {
                        alert.style.opacity -= 0.1;
                    } else {
                        clearInterval(fadeEffect);
                        alert.style.display = 'none';
                    }
                }, 50);
            }
        }, 5000);
    });
});
