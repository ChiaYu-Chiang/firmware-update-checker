"""
此json_to_db.py用於將原有的json檔案轉換成資料庫儲存的格式
"""
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from brands.databases.database import Target


with open("models.json", encoding="utf-8") as file:
    data = json.load(file)

engine = create_engine("sqlite:///brands/databases/firmwares.sqlite")
Session = sessionmaker(bind=engine)
session = Session()

for item in data:
    brand = item["brand"]
    models = item["models"]
    for model in models:
        if model["url_model"]:
            url_model = model["url_model"]

            if brand == "cisco":
                model_link = (
                    f"https://software.cisco.com/download/home/{url_model}/release"
                )
            elif brand == "dell":
                model_link = f"https://www.dell.com/support/home/en-us/product-support/product/{url_model}/drivers"
            elif brand == "hp":
                model_link = f"https://support.hpe.com/connect/s/product?language=en_US&ismnp={url_model}&tab=driversAndSoftware"
            elif brand == "ibm":
                model_link = f"https://www.ibm.com/support/fixcentral/{url_model}&&platform=All&function=all"
            elif brand == "juniper":
                model_link = (
                    f"https://support.juniper.net/support/downloads/?p={url_model}"
                )
            elif brand == "qnap":
                model_link = f"https://www.qnap.com/en-us/download?model={url_model}&category=firmware"
            else:
                model_link = "not defined"

            target = Target(brand=brand, model=model["model"], model_link=model_link)
            session.add(target)

session.commit()

session.close()
