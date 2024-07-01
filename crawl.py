import importlib
from datetime import datetime
import os
import sys
import random
from brands.databases.database import Target
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_path, "brands"))

"""
if __name__ == "__main__":
    with open("models.json", "r", encoding="utf-8") as f:
        brands = json.load(f)

    error_models = []
    pool = []

    for brand in brands:
        brand_name = brand["brand"]
        models = brand["models"]
        module = importlib.import_module(f"brands.show_{brand_name}")
        for model in models:
            pool.append((brand_name, model["model"], model["url_model"], module))

    random.shuffle(pool)
    while pool:
        brand_name, model_name, url_name, module = pool.pop()
        earliest_date = "2022-01-01"
        date_after = datetime.strptime(earliest_date, "%Y-%m-%d").date()
        if url_name:
            try:
                print(f"[{brand_name}] [{model_name}] start crawling")
                module.show_model(model_name, url_name, date_after)
            except:
                # 若發生錯誤，將 brand 與 model 加入 error_models
                error_models.append((brand_name, model_name))
        else:
            print(f"[{brand_name}] [{model_name}] dose not have url")

    # 若有錯誤，印出錯誤訊息
    if error_models:
        print("The following models failed to be crawled: ")
        for brand_name, model_name in error_models:
            print(f"{brand_name}, {model_name}")
"""
# The upper comment is the original code, use json to crawl. The following code use database to crawl.

if __name__ == "__main__":
    server = '10.210.31.15:1433'
    database = 'brian'
    username = 'brian'
    password = 'Chief26576688'

    remote_db = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
    engine = create_engine("sqlite:///brands/databases/test.sqlite")
    Session = sessionmaker(bind=remote_db)
    session = Session()
    query = session.query(Target).all()
    session.close()
    error_models = []
    pool = []
    for item in query:
        brand_name = item.brand
        model_name = item.model
        url_name = item.model_link
        module = importlib.import_module(f"brands.show_{brand_name}")
        pool.append((brand_name, model_name, url_name, module))
    random.shuffle(pool)

    while pool:
        brand_name, model_name, url_name, module = pool.pop()
        earliest_date = "2015-01-01"
        date_after = datetime.strptime(earliest_date, "%Y-%m-%d").date()
        if url_name:
            try:
                print(f"[{brand_name}] [{model_name}] start crawling")
                module.show_model(model_name, url_name, date_after)
            except:
                # 若發生錯誤，將 brand 與 model 加入 error_models
                error_models.append((brand_name, model_name))
        else:
            print(f"[{brand_name}] [{model_name}] dose not have url")

    # 若有錯誤，印出錯誤訊息
    if error_models:
        print("The following models failed to be crawled: ")
        for brand_name, model_name in error_models:
            print(f"{brand_name}, {model_name}")
