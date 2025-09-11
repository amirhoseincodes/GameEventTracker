import connexion
import json
import os
from datetime import datetime

from connexion import NoContent

# ثابت‌ها و تنظیمات اولیه
EVENT_FILE = "events.json"  # نام فایل برای ذخیره رویدادها
MAX_EVENTS = 5  # حداکثر تعداد رویدادهای اخیر که نگه می‌داریم


# این همون فانکشن هندلر برای یک endpoint هست
def post_event(body):
    """
    هندلر عمومی برای دریافت رویداد
    body: داده‌های JSON ارسالی از کلاینت
    """
    # اینجا منطق اصلی endpoint رو پیاده کن

    return {"message": "Hello, OpenAPI!", "body": body}


def post_login_event(body):
    """
    هندلر برای رویداد ورود کاربر
    body: شامل userId و clientId کاربر
    """
    # body شامل داده‌ی POST هست (json ورودی)

    # ساخت پیام برای لاگ کردن اطلاعات ورود
    msg_data = (
        f"User {body['userId']} with client id '{body['clientId']}' logged in. "
    )
    # ثبت رویداد ورود در فایل
    log_event("login", msg_data)

    return {"message": "Login event received", "data": body}


def post_score_event(body):
    """
    هندلر برای رویداد امتیازگیری کاربر
    body: شامل userId، clientId، score و levelId
    """
    # body شامل داده‌ی POST هست (json ورودی)

    # ساخت پیام برای لاگ کردن اطلاعات امتیاز
    msg_data = (
        f"User {body['userId']} with client id '{body['clientId']}' scored {body['score']} in level {body['levelId']}. "
    )
    # ثبت رویداد امتیاز در فایل
    log_event("score", msg_data)

    return {"message": "Score event received", "data": body}


def get_health(body):
    """
    هندلر برای بررسی سلامت سرویس (health check)
    body: داده‌های دریافتی (معمولاً خالی)
    """
    # body شامل داده‌ی POST هست (json ورودی)
    return {"message": "Health event received", "data": body}


def load_event_data():
    """
    بارگیری داده‌های رویداد از فایل JSON
    اگر فایل وجود نداشته باشد، ساختار اولیه را برمی‌گرداند
    """
    if os.path.exists(EVENT_FILE):
        # اگر فایل موجود باشد، محتوای آن را بخوان
        with open(EVENT_FILE, "r") as f:
            return json.load(f)
    else:
        # اگر فایل وجود نداشته باشد، ساختار اولیه را برگردان
        return {
            "num_logins": 0,  # تعداد کل ورودها
            "recent_logins": [],  # لیست ورودهای اخیر
            "num_scores": 0,  # تعداد کل امتیازها
            "recent_scores": []  # لیست امتیازهای اخیر
        }


def save_event_data(data):
    """
    ذخیره داده‌های رویداد در فایل JSON
    data: دیکشنری حاوی تمام داده‌های رویدادها
    """
    with open(EVENT_FILE, "w") as f:
        # ذخیره داده‌ها با فرمت زیبا (indent=4)
        json.dump(data, f, indent=4)


def log_event(event_type, event_message):
    """
    ثبت یک رویداد در فایل JSON
    event_type: نوع رویداد ("login" یا "score")
    event_message: پیام توضیحی رویداد
    """
    # بارگیری داده‌های موجود
    data = load_event_data()

    # ساخت تایم استمپ فعلی با دقت میکروثانیه
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # ساخت آبجکت رویداد
    event = {
        "msg_data": event_message,  # پیام رویداد
        "received_timestamp": timestamp  # زمان دریافت
    }

    # بروزرسانی داده‌ها بر اساس نوع رویداد
    if event_type == "login":
        # افزایش شمارنده ورودها
        data["num_logins"] += 1
        # اضافه کردن رویداد جدید به ابتدای لیست
        data["recent_logins"].insert(0, event)
        # حذف رویدادهای اضافی اگر از حد مجاز بیشتر شد
        if len(data["recent_logins"]) > MAX_EVENTS:
            data["recent_logins"].pop()

    elif event_type == "score":
        # افزایش شمارنده امتیازها
        data["num_scores"] += 1
        # اضافه کردن رویداد جدید به ابتدای لیست
        data["recent_scores"].insert(0, event)
        # حذف رویدادهای اضافی اگر از حد مجاز بیشتر شد
        if len(data["recent_scores"]) > MAX_EVENTS:
            data["recent_scores"].pop()

    # ذخیره داده‌های بروزرسانی شده
    save_event_data(data)

    # نمایش رویداد ثبت شده در کنسول
    print("Logged:", json.dumps(event, indent=4))


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