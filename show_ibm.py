from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from database import Session, Driver
import re

brand = "ibm"
model = "System x3250 M3"

# 設定 webdriver 參數
options = Options()
# options.add_argument("headless")
options.add_argument("window-size=1920,1080")

# 啟動瀏覽器
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 30)

urls = [
    "https://www.ibm.com/support/fixcentral/systemx/selectFixes?parent=System%20x3250%20M3&product=ibm/systemx/4251_brocade&&platform=All&function=all",
    "https://www.ibm.com/support/fixcentral/systemx/selectFixes?parent=System%20x3250%20M3&product=ibm/systemx/4251&&platform=All&function=all",
]

for url in urls:
    # 訪問網頁
    browser.get(url)

    # 等待元素出現
    element = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/div[1]/div[4]/main/div/div/div/div/div[1]/div[1]/div/div[2]/form[2]/div/div/div",
            )
        )
    )

    # 定位目標元素
    contents = element.find_elements(By.XPATH, "div/div/table/tbody/tr")

    # 創建 Session 實例
    session = Session()

    # 遍歷每組資料
    print("Start crawling")
    for content in contents:
        element = content.find_element(
            By.XPATH,
            "td[2]/div[1]",
        )
        browser.execute_script("arguments[0].style.display='block'", element)

        # 取得資料
        title = content.find_element(By.XPATH, "td[2]/p").text.split("\n")[-1]
        version = (
            element.find_element(By.XPATH, "p[2]")
            .text.replace("Upgrades to:", "")
            .strip()
        )
        importance = (
            element.find_element(By.XPATH, "p[3]").text.replace("Severity:", "").strip()
        )
        category = (
            element.find_element(By.XPATH, "p[4]")
            .text.replace("Component:", "")
            .strip()
        )
        release_date = content.find_element(By.XPATH, "td[3]").text
        description = (
            element.find_element(By.XPATH, "p[5]").text.replace("Abstract:", "").strip()
        )
        important_information = content.find_element(By.XPATH, "td[2]/p/a").text

        # 資料格式處理
        release_date = datetime.strptime(release_date, "%Y/%m/%d").date()

        # 判斷資料是否已抓過
        record = (
            session.query(Driver)
            .filter_by(brand=brand, model=model, title=title, version=version)
            .first()
        )
        if record:
            if record.title == title and record.version == version:
                print("Data already exist")
                continue

        # 寫入至資料庫
        print(f"new data: {title}")
        driver = Driver(
            brand=brand,
            model=model,
            title=title,
            version=version,
            importance=importance,
            category=category,
            release_date=release_date,
            # download_link=download_link,
            description=description,
            important_information=important_information,
            # crawler_info=crawler_info,
        )
        session.add(driver)
        session.commit()

    # 關閉連線
    session.close()

# 等待使用者手動關閉瀏覽器
print("Exiting browser")
# input("Press any key to close the browser...")
browser.quit()
