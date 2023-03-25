from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from brands.databases.database import Driver
from logging.handlers import TimedRotatingFileHandler, HTTPHandler
import logging
from brands.databases.notifications.notification import send_line_notification


app = Flask(__name__)
bootstrap = Bootstrap5(app)

# 建立資料庫連線
engine = create_engine("sqlite:///brands/databases/firmwares.sqlite")
Session = sessionmaker(bind=engine)


class LineNotifyHandler(logging.Handler):
    def emit(self, record):
        message = self.format(record)
        send_line_notification(message)


# 設定日誌
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)-15s - %(levelname)-8s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log_handler = TimedRotatingFileHandler("logs/app.log", when="midnight", interval=1)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

http_handler = HTTPHandler(host="", url="", method="POST")
http_handler.setLevel(logging.WARNING)

line_notify_handler = LineNotifyHandler()
line_notify_handler.setLevel(logging.WARNING)
logger.addHandler(line_notify_handler)


# 日誌紀錄和發送 LINE Notify
@app.after_request
def get_status_code(response):
    user_ip = request.headers.get("X-Forwarded-For", "127.0.0.1")
    status_code = response.status
    message = f"Request: method={request.method}, status={status_code}, path={request.path}, user_ip={user_ip}"
    logger.info(message)
    return response


@app.route("/")
def index():
    # 取得篩選條件
    brand = request.args.get("brand", default="", type=str)
    model = request.args.get("model", default="", type=str)
    search = request.args.get("search", default="", type=str)
    importance = request.args.get("importance", default="", type=str)

    # 建立資料庫session
    session = Session()

    # 建立查詢物件
    query = session.query(Driver).order_by(Driver.release_date.desc())

    # 篩選品牌
    if brand and brand != "All":
        query = query.filter(Driver.brand == brand)

    # 篩選型號
    if model:
        query = query.filter(Driver.model == model)

    # 篩選重要性
    if importance and importance != "All":
        if importance == "None":
            query = query.filter(Driver.importance == None)
        else:
            query = query.filter(Driver.importance == importance)

    # 篩選標題、描述、重要資訊
    if search:
        query = query.filter(
            or_(
                Driver.title.ilike(f"%{search}%"),
                Driver.description.ilike(f"%{search}%"),
                Driver.important_information.ilike(f"%{search}%"),
            )
        )

    # 取得結果
    drivers = query.all()

    # 取得品牌清單
    brands = session.query(Driver.brand).distinct().all()

    # 取得型號清單
    models = session.query(Driver.model, Driver.brand).distinct().all()

    # 取得重要性清單
    importances = session.query(Driver.importance).distinct().all()

    # 關閉session
    session.close()

    # 傳送結果到template
    return render_template(
        "index.html",
        drivers=drivers,
        brands=brands,
        models=models,
        importances=importances,
        brand=brand,
        model=model,
        importance=importance,
        search=search,
    )


# 測試發送warning級別的日誌
@app.route("/test_notification")
def test_notification():
    logger.warning("Test notification")
    return "Test notification"


if __name__ == "__main__":
    app.run()
