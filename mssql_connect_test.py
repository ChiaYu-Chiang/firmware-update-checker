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

remote_db = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
# 建立資料表
Base.metadata.create_all(remote_db)

# 建立 session 類別
Session = sessionmaker(bind=remote_db)


