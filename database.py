from sqlalchemy import create_engine, Column, Integer, String, Date, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import requests
import smtplib
from email.mime.text import MIMEText

line_notify_access_token = os.environ.get("line_notify_access_token")

# 定義資料表的抽象類別
Base = declarative_base()


# 定義資料表
class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String)
    model = Column(String)
    title = Column(String)
    version = Column(String)
    importance = Column(String)
    category = Column(String)
    release_date = Column(Date)
    download_link = Column(String)
    description = Column(String)
    important_information = Column(String)
    crawler_info = Column(String)


# 定義連接引擎
engine = create_engine("sqlite:///firmwares.sqlite")
test = create_engine("sqlite:///test.sqlite")
# 建立資料表
Base.metadata.create_all(test)

# 建立 session 類別
Session = sessionmaker(bind=test)


# 設定 email
def send_email_notification(message):
    email = "you@example.com"
    password = "your_email_password"
    to_email = "recipient@example.com"

    msg = MIMEText(message)
    msg["Subject"] = "New data committed"
    msg["From"] = email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.send_message(msg)
    server.quit()


# 監聽事件
@event.listens_for(Session, "before_commit")
def receive_after_commit(session):
    for obj in session.new:
        message = "brand={}\nmodel={}\ntitle={}\nversion={}\nimportance={}\ncategory={}\nrelease_date={}".format(
            obj.brand,
            obj.model,
            obj.title,
            obj.version,
            obj.importance,
            obj.category,
            obj.release_date,
        )

    # 透過 line notify 發送
    headers = {
        "Authorization": "Bearer " + line_notify_access_token,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {"message": message}
    # requests.post(
    #     "https://notify-api.line.me/api/notify", headers=headers, params=params
    # )

    # # 透過 email 發送
    # send_email_notification(message)
