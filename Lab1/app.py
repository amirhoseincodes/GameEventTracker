import connexion

from connexion import NoContent


# این همون فانکشن هندلر برای یک endpoint هست
def postEvent(body):
    # اینجا منطق اصلی endpoint رو پیاده کن
    return {"message": "Hello, OpenAPI!", "body": body}


def postLoginEvent(body):
    # body شامل داده‌ی POST هست (json ورودی)
    return {"message": "Login event received", "data": body}

def postScoreEvent(body):
    # body شامل داده‌ی POST هست (json ورودی)
    return {"message": "Source event received", "data": body}

def getHealth(body):
    # body شامل داده‌ی POST هست (json ورودی)
    return {"message": "Health event received", "data": body}


# ساختن app در سطح ماژول
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

if __name__ == "__main__":
    app.run(port=8080)
