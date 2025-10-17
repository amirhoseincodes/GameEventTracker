import functools
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from event import *
import yaml
import connexion
import logging.config
from datetime import datetime

from datetime import datetime

def parse_iso8601(ts: str):
    try:
        # رشته را تمیز می‌کنیم
        ts = ts.strip()
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        return None



# لود کردن تنظیمات از فایل کانفیگ و لغو کردن هارد کد
with open('app-conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# استفاده از تنظیمات برای گرفتن لاگ ها
with open("log-conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

# ساخت موتور دیتابیس SQLite

engine = create_engine(f"mysql+pymysql://{app_config['user']}:{app_config['password']}@{app_config['hostname']}/{app_config['db']}")


def make_session():
    """تابع برای ساخت یک نشست (session) جدید دیتابیس"""
    return sessionmaker(bind=engine)()


def create_table():
    """تابع برای ساخت تمام جداول در دیتابیس"""
    Base.metadata.create_all(bind=engine)


def drop_table():
    """تابع برای حذف تمام جداول از دیتابیس"""
    Base.metadata.drop_all(bind=engine)


def use_db_session(func):
    """دکوریتر برای مدیریت خودکار نشست دیتابیس"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # ساخت نشست جدید
        session = make_session()
        try:
            # اجرای تابع با ارسال session به عنوان اولین پارامتر
            return func(session, *args, **kwargs)
        finally:
            # بستن نشست در پایان (حتی در صورت بروز خطا)
            session.close()

    return wrapper


@use_db_session
def add_login_event(session, body):
    """تابع برای افزودن رویداد ورود کاربر به دیتابیس"""
    # ساخت شیء LoginReport با اطلاعات دریافتی
    event = LoginReport(
        trace_id=body["trace_id"], # آی دی رصد و پیگیری
        user_id=body["user_id"],  # شناسه کاربر
        client_id=body["client_id"],  # شناسه کلاینت
        event_id=body.get("event_id", ""),  # شناسه رویداد (اختیاری)
        platform=body.get("platform", ""),  # پلتفرم (اختیاری)
        local=body.get("local", ""),  # منطقه محلی (اختیاری)
        ip=body.get("ip", ""),  # آدرس IP (اختیاری)
        timestamp=datetime.now(),  # زمان فعلی
    )

    # افزودن رویداد به نشست و ذخیره در دیتابیس
    session.add(event)
    session.commit()

    # بازگشت پیام موفقیت همراه با داده‌های دریافتی
    return {"message": "Login event saved", "data": body}


@use_db_session
def add_score_event(session, body):
    """تابع برای افزودن رویداد امتیاز کاربر به دیتابیس"""
    # ساخت شیء ScoreReport با اطلاعات دریافتی
    event = ScoreReport(
        trace_id=body["trace_id"],  # آی دی رصد و پیگیری
        user_id=body["user_id"],  # شناسه کاربر
        client_id=body["client_id"],  # شناسه کلاینت
        event_id=body.get("event_id", ""),  # شناسه رویداد (اختیاری)
        level_id=body["level_id"],  # شناسه مرحله بازی
        score=body["score"],  # امتیاز کسب شده
        duration_ms=body["duration_ms"],  # مدت زمان بازی (میلی‌ثانیه)
        timestamp=datetime.now(),  # زمان فعلی
    )

    # افزودن رویداد به نشست و ذخیره در دیتابیس
    session.add(event)
    session.commit()

    # بازگشت پیام موفقیت همراه با داده‌های دریافتی
    return {"message": "Score event stored in DB", "data": body}




def post_login_event(body):
    """تابع برای دریافت درخواست ثبت رویداد ورود کاربر"""
    # اگر جداول هنوز ساخته نشده‌اند، آن‌ها را بساز

    trace_id = body["trace_id"]
    store_report = f"Stored event login_report with a trace id of {trace_id}"
    logger.info(store_report)

    # وارد کردن تابع از ماژول اصلی و فراخوانی آن
    return add_login_event(body)


def post_score_event(body):
    """تابع برای دریافت درخواست ثبت رویداد امتیاز کاربر"""
    # اگر جداول هنوز ساخته نشده‌اند، آن‌ها را بساز

    trace_id = body["trace_id"]
    store_report = f"Stored event score_report with a trace id of {trace_id}"
    logger.info(store_report)

    # وارد کردن تابع از ماژول اصلی و فراخوانی آن
    return add_score_event(body)

from flask import request, jsonify

# ------------------------ #
#   GET /login_report      #
# ------------------------ #
@use_db_session
def get_login_events(session):
    """دریافت تمام رویدادهای ورود در بازه زمانی مشخص"""
    start_ts = request.args.get("start_timestamp")
    end_ts = request.args.get("end_timestamp")

    if not start_ts or not end_ts:
        return {"message": "start_timestamp and end_timestamp are required"}, 400

    try:
        start_dt = parse_iso8601(start_ts)
        end_dt = parse_iso8601(end_ts)
    except Exception:
        return {"message": "Invalid datetime format"}, 400

    if not start_dt or not end_dt:
        return {"message": "Invalid datetime format"}, 400

    # فیلتر کردن بر اساس بازه زمانی
    events = (
        session.query(LoginReport)
        .filter(LoginReport.timestamp >= start_dt, LoginReport.timestamp < end_dt)
        .all()
    )

    # تبدیل به JSON
    results = [
        {
            "trace_id": e.trace_id,
            "user_id": e.user_id,
            "client_id": e.client_id,
            "event_id": e.event_id,
            "platform": e.platform,
            "local": e.local,
            "ip": e.ip,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in events
    ]

    logger.info(f"Returned {len(results)} login events from DB.")
    return jsonify(results), 200


# ------------------------ #
#   GET /score_report      #
# ------------------------ #
@use_db_session
def get_score_events(session):
    """دریافت تمام رویدادهای امتیاز در بازه زمانی مشخص"""
    start_ts = request.args.get("start_timestamp")
    end_ts = request.args.get("end_timestamp")

    if not start_ts or not end_ts:
        return {"message": "start_timestamp and end_timestamp are required"}, 400

    try:
        start_dt = parse_iso8601(start_ts)
        end_dt = parse_iso8601(end_ts)
    except Exception:
        return {"message": "Invalid datetime format"}, 400

    if not start_dt or not end_dt:
        return {"message": "Invalid datetime format"}, 400


    events = (
        session.query(ScoreReport)
        .filter(ScoreReport.timestamp >= start_dt, ScoreReport.timestamp < end_dt)
        .all()
    )

    results = [
        {
            "trace_id": e.trace_id,
            "user_id": e.user_id,
            "client_id": e.client_id,
            "event_id": e.event_id,
            "level_id": e.level_id,
            "score": e.score,
            "duration_ms": e.duration_ms,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in events
    ]

    logger.info(f"Returned {len(results)} score events from DB.")
    return jsonify(results), 200


# ساخت اپلیکیشن Connexion (که بر پایه Flask است)
app = connexion.FlaskApp(__name__, specification_dir='')

# اضافه کردن API از فایل مشخصات OpenAPI YAML
app.add_api(
    "openapi.yml",  # فایل مشخصات OpenAPI
    strict_validation=True,  # فعال کردن اعتبارسنجی سخت‌گیرانه درخواست‌ها
    validate_responses=True  # فعال کردن اعتبارسنجی پاسخ‌ها
)

# اجرای اپلیکیشن اگر این فایل به صورت مستقیم اجرا شود
if __name__ == "__main__":
  #  drop_table()                  # همه جدول‌ها حذف میشه

    Base.metadata.create_all(engine)
    app.run(port=8090)  # اجرا روی پورت 8090

