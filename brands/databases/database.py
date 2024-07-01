from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    event,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from brands.databases.notifications.notification import (
    send_line_notification,
    send_email_notification,
)
from datetime import datetime

# 定義資料表的抽象類別
Base = declarative_base()


# 定義資料表
class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String(255))
    model = Column(String(255))
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


class Target(Base):
    __tablename__ = "targets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String(255))
    model = Column(String(255))
    model_link = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    # brand, model 組合為 unique
    __table_args__ = (UniqueConstraint("brand", "model", name="_brand_model_uc"),)


# 定義連接引擎
server = '10.210.31.15:1433'
database = 'brian'
username = 'brian'
password = 'Chief26576688'

engine = create_engine("sqlite:///brands/databases/firmwares.sqlite")
test = create_engine("sqlite:///brands/databases/test.sqlite")
remote_db = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
# 建立資料表
Base.metadata.create_all(remote_db)

# 建立 session 類別
Session = sessionmaker(bind=remote_db)


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

        email_message = f"""
        <html>
            <head>
                <style>
                    table {{
                        border-collapse: collapse;
                        width: 80%;
                        margin: auto;
                    }}
                    th, td {{
                        text-align: left;
                        padding: 8px;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    th {{
                        background-color: #4CAF50;
                        color: white;
                    }}
                    .long-col {{
                        width: 30%;
                        word-wrap: break-word;
                    }}
                </style>
            </head>
            <body>
                <table>
                    <tr>
                        <th>品牌</th>
                        <th>型號</th>
                        <th>標題</th>
                        <th>版本</th>
                        <th>重要性</th>
                        <th>類別</th>
                        <th>釋出日期</th>
                        <th>下載連結</th>
                        <th class="long-col">描述</th>
                        <th class="long-col">重要資訊</th>
                    </tr>
                    <tr>
                        <td>{obj.brand}</td>
                        <td><a href="{obj.model_link}">{obj.model}</a></td>
                        <td class="long-col">{obj.title}</td>
                        <td>{obj.version}</td>
                        <td>{obj.importance}</td>
                        <td>{obj.category}</td>
                        <td>{obj.release_date}</td>
                        <td><a href="{obj.download_link}">下載</a></td>
                        <td class="long-col">{obj.description}</td>
                        <td class="long-col">{obj.important_information}</td>
                    </tr>
                </table>
            </body>
        </html>
        """

    # send_email_notification(email_message)
    # send_line_notification(message)
