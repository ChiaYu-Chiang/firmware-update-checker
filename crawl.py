import json
import importlib
import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_path, "brands"))

# 讀取 models.json 檔案
with open("models.json", "r") as f:
    brands = json.load(f)

for brand in brands:
    # 取得 brand 名稱
    brand_name = brand["brand"]

    # 匯入品牌的 Python 模組
    module = importlib.import_module(f"brands.show_{brand_name}")

    # 取得該品牌的所有 models
    models = brand["models"]

    for model in models:
        # 取得 model 名稱
        model_name = model["model"]
        url_name = model["url_model"]

        if url_name:
            module.show_model(model_name, url_name)
        else:
            print(
                "[{}] [{}] dose not have url".format(
                    brand_name,
                    model_name,
                )
            )
            continue
