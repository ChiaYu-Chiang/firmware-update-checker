from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from database import Session, Driver

brand = "gigabyte"
model = "R182-340"

# 設定 webdriver 參數
options = Options()
options.add_argument("headless")
options.add_argument("window-size=1920,1080")

# 啟動瀏覽器
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)

# 訪問網頁
browser.get(
    "https://www.gigabyte.com/tw/Enterprise/Rack-Server/R182-340-rev-100#Support-Firmware"
)

# 等待資料顯式
element = wait.until(
    EC.visibility_of_element_located(
        (By.XPATH, '//*[@id="Section-Support"]/div/div[2]/div/div[4]')
    )
)

# 定位目標元素
contents = element.find_elements(By.XPATH, "div/div[2]/div[2]")

# 創建 Session 實例
session = Session()

# 遍歷每組資料
print("Start crawling")
for content in contents:
    # 取得資料
    name = content.find_element(
        By.XPATH,
        "div[1]",
    ).text
    version = content.find_element(
        By.XPATH,
        "div[2]",
    ).text
    release_date = content.find_element(
        By.XPATH,
        "div[4]",
    ).text
    download_link = content.find_element(
        By.XPATH,
        "div[5]/a",
    ).get_attribute("href")

    # 資料格式處理
    release_date = datetime.strptime(release_date, "%Y/%m/%d").date()

    # 判斷資料是否已抓過
    record = session.query(Driver).filter_by(brand=brand, model=model).first()
    if record:
        if record.name == name and record.version == version:
            print("Data already exist")
            continue

    # 寫入至資料庫
    print(f"new data: {name}")
    driver = Driver(
        brand=brand,
        model=model,
        name=name,
        version=version,
        # importance=importance,
        # category=category,
        release_date=release_date,
        download_link=download_link,
        # description=description,
        # important_information=important_information,
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
