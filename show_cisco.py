from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from database import Session, Driver

brand = "cisco"
model = "Catalyst 2960S-24TS-S Switch"

# 設定 webdriver 參數
options = Options()
options.add_argument("headless")
options.add_argument("window-size=1920,1080")

# 啟動瀏覽器
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 30)

# 訪問網頁
browser.get("https://software.cisco.com/download/home/282867583/type/280805680/release")

# 等待元素出現
element = wait.until(
    EC.visibility_of_element_located(
        (
            By.XPATH,
            '//*[@id="fw-content"]/div/div/app-release-page/div/div[2]/app-image-details/div[2]/div[2]',
        )
    )
)

# 定位目標元素
contents = element.find_elements(By.XPATH, "div/div")

# 創建 Session 實例
session = Session()

# 遍歷每組資料
print("Start crawling")
for content in contents:
    # 取得資料
    title = content.find_element(By.XPATH, "div/div[1]/div[1]/div/span").text
    version = browser.find_element(By.XPATH, '//*[@id="release-version-title"]').text
    release_date = content.find_element(By.XPATH, "div/div[2]").text
    crawler_info = content.find_element(By.XPATH, "div/div[1]/div[2]/span").text

    # 資料格式處理
    release_date = datetime.strptime(release_date, "%d-%b-%Y").date()

    # 判斷資料是否已抓過
    record = (
        session.query(Driver)
        .filter_by(brand=brand, model=model, title=title, version=version)
        .first()
    )
    if record:
        if record.crawler_info == crawler_info:
            print("Data already exist")
            continue

    # 寫入至資料庫
    print(f"new data: {title}")
    driver = Driver(
        brand=brand,
        model=model,
        title=title,
        version=version,
        # importance=importance,
        # category=category,
        release_date=release_date,
        # download_link=download_link,
        # description=description,
        # important_information=important_information,
        crawler_info=crawler_info,
    )
    session.add(driver)
    session.commit()

# 關閉連線
session.close()

# 等待使用者手動關閉瀏覽器
print("Exiting browser")
# input("Press any key to close the browser...")
browser.quit()
