from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from brands.databases.database import Driver, Target
from logging.handlers import TimedRotatingFileHandler, HTTPHandler
from werkzeug.exceptions import HTTPException
import logging, ssl
from brands.databases.notifications.notification import send_line_notification
from sqlalchemy.exc import IntegrityError
from urllib.request import urlopen
import importlib, os, sys
from datetime import datetime
from threading import Thread

# importlib所需的路徑匯入
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_path, "brands"))

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# 建立資料庫連線
server = ''
database = 'brian'
username = 'brian'
password = ''

remote_db = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
engine = create_engine("sqlite:///brands/databases/test.sqlite")
Session = sessionmaker(bind=remote_db)

def start_crawl(brand, model, model_link):
    try:
        print(f"start crawling {brand} {model}")
        earliest_date = "2015-01-01"
        date_after = datetime.strptime(earliest_date, "%Y-%m-%d").date()
        module = importlib.import_module(f"show_{brand}")
        module.show_model(model, model_link, date_after)
    except Exception as e:
        print(f"execute {brand} {model} crawl fail: {e}")

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


@app.route("/add_model", methods=["GET", "POST"])
def add_model():
    if request.method == "POST":
        brand = request.form.get("brand").lower()
        if brand == "other":
            brand = request.form.get("other_brand").lower()
        model = request.form.get("model")
        model_link = request.form.get("model_link")
        session = Session()
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            urlopen(model_link)
            try:
                driver = Target(brand=brand, model=model, model_link=model_link)
                session.add(driver)
                session.commit()
                message = "新增成功"
                # 新增後直接執行爬蟲
                crawl_thread = Thread(target=start_crawl, args=(brand, model, model_link))
                crawl_thread.start()
            except IntegrityError:
                session.rollback()
                message = "此筆資料已經存在"
        except:
            message = "請確認網址是否正確"
        brands = session.query(Target.brand).distinct().all()
        session.close()
        brands = [brand[0] for brand in brands if brand[0]]
        return render_template("add_model.html", brands=brands, message=message)
    session = Session()
    brands = session.query(Target.brand).distinct().all()
    session.close()
    brands = [brand[0] for brand in brands if brand[0]]
    return render_template("add_model.html", brands=brands)


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


@app.errorhandler(403)
def forbidden(error):
    message = "You are not allowed to access this page."
    return render_template("403.html", message=message), 403


@app.errorhandler(404)
def page_not_found(error):
    message = "This page dose not exist."
    return render_template("404.html", message=message), 404


@app.errorhandler(Exception)
def app_errorhandler(e):
    if isinstance(e, HTTPException):
        return e
    message = "Oops! Something went wrong. Please come back in a while."
    return render_template("500.html", message=message), 500


# 測試發送warning級別的日誌
@app.route("/test_notification")
def test_notification():
    logger.warning("Test notification")
    return "Test notification"


if __name__ == "__main__":
    app.run()
