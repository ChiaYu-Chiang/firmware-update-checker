from flask import Flask, render_template, request
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from brands.databases.database import Driver

app = Flask(__name__)

# 建立資料庫連線
engine = create_engine("sqlite:///brands/databases/test.sqlite")
Session = sessionmaker(bind=engine)


@app.route("/")
def index():
    # 取得篩選條件
    brand = request.args.get("brand", default="", type=str)
    model = request.args.get("model", default="", type=str)

    # 建立資料庫session
    session = Session()

    # 建立查詢物件，使用order_by方法排序
    query = session.query(Driver).order_by(Driver.release_date.desc())

    # 篩選品牌
    if brand and brand != "All":
        query = query.filter(Driver.brand == brand)

    # 篩選型號
    if model:
        query = query.filter(Driver.model == model)

    # 取得結果
    drivers = query.all()

    # 取得品牌清單
    brands = session.query(Driver.brand).distinct().all()

    # 取得型號清單
    models = session.query(Driver.model, Driver.brand).distinct().all()

    # 關閉session
    session.close()

    # 傳送結果到template
    return render_template(
        "index.html",
        drivers=drivers,
        brands=brands,
        models=models,
        brand=brand,
        model=model,
    )


if __name__ == "__main__":
    app.run()
