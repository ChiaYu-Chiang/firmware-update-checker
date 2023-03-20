from sqlalchemy import create_engine, Column, Integer, String, Date, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from brands.databases.notifications.notification import (
    send_line_notification,
    send_email_notification,
)

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
    model_link = Column(String)


# 定義連接引擎
engine = create_engine("sqlite:///brands/databases/firmwares.sqlite")
test = create_engine("sqlite:///brands/databases/test.sqlite")
# 建立資料表
Base.metadata.create_all(engine)

# 建立 session 類別
Session = sessionmaker(bind=engine)


# 監聽事件，當資料庫 commit 時，發送通知
@event.listens_for(Session, "before_commit")
def receive_after_commit(session):
    for obj in session.new:
        message = f"""
        這是來自Firmware_Crawler的通知,以下是最新取得的資料:
        brand={obj.brand}
        model={obj.model}
        model_link={obj.model_link}
        title={obj.title}
        version={obj.version}
        importance={obj.importance}
        category={obj.category}
        release_date={obj.release_date}
        download_link={obj.download_link}
        description={obj.description}
        important_information={obj.important_information}"""

    send_email_notification(message)
    send_line_notification(message)
