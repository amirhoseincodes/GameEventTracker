import functools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from event import *

import connexion
from datetime import datetime

# متغیر برای کنترل ساخت جداول دیتابیس
created = False


# ساخت موتور دیتابیس SQLite
engine = create_engine("sqlite:///game_tracker_engine.db")


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
        user_id=body["userId"],  # شناسه کاربر
        client_id=body["clientId"],  # شناسه کلاینت
        event_id=body.get("eventId", ""),  # شناسه رویداد (اختیاری)
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
        user_id=body["userId"],  # شناسه کاربر
        client_id=body["clientId"],  # شناسه کلاینت
        event_id=body.get("eventId", ""),  # شناسه رویداد (اختیاری)
        level_id=body["levelId"],  # شناسه مرحله بازی
        score=body["score"],  # امتیاز کسب شده
        duration_ms=body["durationMs"],  # مدت زمان بازی (میلی‌ثانیه)
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
    if not created:
        Base.metadata.create_all(engine)
    # وارد کردن تابع از ماژول اصلی و فراخوانی آن
    return add_login_event(body)


def post_score_event(body):
    """تابع برای دریافت درخواست ثبت رویداد امتیاز کاربر"""
    # اگر جداول هنوز ساخته نشده‌اند، آن‌ها را بساز
    if not created:
        Base.metadata.create_all(engine)
    # وارد کردن تابع از ماژول اصلی و فراخوانی آن
    return add_score_event(body)

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
    app.run(port=8090)  # اجرا روی پورت 8090