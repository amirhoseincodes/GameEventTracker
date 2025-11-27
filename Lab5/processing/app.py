import connexion
import httpx
from connexion import NoContent
import yaml
import uuid
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler

# استفاده از کانفیگ جداگانه برای بارگذاری تنظیمات
with open('app-conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# استفاده از تنظیمات برای گرفتن لاگ ها
with open("log-conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')


def get_stats(body):
    """
    بالاترین امتیاز کاربر را برمی گرداند.
    :param body:
    :return:
    """
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    event_id = body["event_id"]

    storage_url = f"{app_config['events']['login']['url']}"
    r = httpx.get(storage_url)

    trace_report = f"Received event login_report with a trace id of {trace_id}"
    response_report = f"Response for event login_report {event_id} has status {r.status_code}"
    logger.info(trace_report)
    logger.info(response_report)

    return r

def populate_stats():
    # print("In function populate stats!")
    logger.info("In function populate stats!")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        populate_stats,
        'interval',
        seconds=app_config['scheduler']['interval']
    )
    sched.start()
    print("Scheduler started!")

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
    init_scheduler()
    app.run(port=8100)  # اجرا روی پورت 8100