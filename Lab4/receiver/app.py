import connexion
import httpx
from connexion import NoContent
import yaml
import uuid

# STORAGE_URL = "http://localhost:8090"  # Storage  service

# استفاده از کانفیگ جداگانه برای بارگذاری تنظیمات
with open('app-conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


def post_login_event(body):
    """Forward login event to storage service"""
    body["trace_id"] = str(uuid.uuid4())
    # r = httpx.post(f"{STORAGE_URL}/events/login", json=body) روش قبلی جاگذاری مسیر
    storage_url = f"{app_config['events']['login']['url']}"
    r = httpx.post(storage_url, json=body)

    # بازگرداندن همان status code که storage داده و بدون content
    return NoContent, r.status_code


def post_score_event(body):
    """Forward score event to storage service"""
    body["trace_id"] = str(uuid.uuid4())
    # r = httpx.post(f"{STORAGE_URL}/events/score", json=body)
    storage_url = f"{app_config['events']['score']['url']}"
    r = httpx.post(storage_url, json=body)

    return NoContent, r.status_code


# این همون فانکشن هندلر برای یک endpoint هست
def post_event(body):
    """
    هندلر عمومی برای دریافت رویداد
    body: داده‌های JSON ارسالی از کلاینت
    """
    # اینجا منطق اصلی endpoint رو پیاده کن

    return {"message": "Hello, OpenAPI!", "body": body}



def get_health(body):
    """
    هندلر برای بررسی سلامت سرویس (health check)
    body: داده‌های دریافتی (معمولاً خالی)
    """
    # body شامل داده‌ی POST هست (json ورودی)
    return {"message": "Health event received", "data": body}




# ساختن اپلیکیشن Connexion در سطح ماژول
app = connexion.FlaskApp(__name__, specification_dir='')

# اضافه کردن API از فایل OpenAPI YAML
app.add_api(
    "openapi.yml",  # فایل مشخصات OpenAPI
    strict_validation=True,  # فعال کردن اعتبارسنجی سخت‌گیرانه
    validate_responses=True  # فعال کردن اعتبارسنجی پاسخ‌ها
)

# اجرای اپلیکیشن اگر این فایل به صورت مستقیم اجرا شود
if __name__ == "__main__":

    app.run(port=8080)  # اجرا روی پورت 8080