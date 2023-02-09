from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from database import Session, Driver

brand = "dell"
model = "PowerEdge R740"

# 設定 webdriver 參數
options = Options()
options.add_argument("headless")
options.add_argument("window-size=1920,1080")

# 啟動瀏覽器
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)

# 訪問網頁
browser.get(
    "https://www.dell.com/support/home/en-us/product-support/product/poweredge-r740/drivers"
)

# 找到下拉式選單
element = wait.until(EC.element_to_be_clickable((By.ID, "operating-system")))

# 選擇 option value="NAA" 的選項
select = Select(element)
select.select_by_value("NAA")

# 等待按鈕元素出現
show_all_button = wait.until(EC.element_to_be_clickable((By.ID, "paginationRow")))

# 點擊按鈕
show_all_button.click()

# 定位按鈕元素
buttons = browser.find_elements(By.NAME, "btnDriverListToggle")

# 創建 Session 實例
session = Session()

# 點擊每個按鈕
print("Start crawling")
for button in buttons:
    tr_id = button.find_element(By.XPATH, "../..").get_attribute("id").split("_")[1]

    # 判斷資料是否已抓過
    record = (
        session.query(Driver)
        .filter_by(brand=brand, model=model, crawler_info=tr_id)
        .first()
    )
    if record:
        if record.crawler_info == tr_id:
            print("Data already exist")
            continue

    # 點擊按鈕
    button.click()

    # 等待資料顯示出來
    child_tr = wait.until(EC.presence_of_element_located((By.ID, f"child_{tr_id}")))

    # 定位節點
    tableRow_point = button.find_element(By.XPATH, f'//tr[@id="tableRow_{tr_id}"]')
    child_point = button.find_element(
        By.XPATH, f'//tr[@id="child_{tr_id}"]/td[2]/section'
    )

    # 取得資料
    name = tableRow_point.find_element(By.XPATH, "td[2]/div/div[2]").text
    version = child_point.find_element(By.XPATH, "div[5]/div[1]/p[2]").text
    importance = tableRow_point.find_element(By.XPATH, "td[3]/span").text
    category = tableRow_point.find_element(By.XPATH, "td[4]").text
    release_date = tableRow_point.find_element(By.XPATH, "td[5]").text
    download_link = tableRow_point.find_element(
        By.XPATH, "td[6]/div/a[2]"
    ).get_attribute("href")
    description = child_point.find_element(By.XPATH, "div[7]/p[2]").text
    try:
        important_information = child_point.find_element(By.XPATH, "div[8]/p[2]").text
    except NoSuchElementException:
        important_information = None

    # 資料格式處理
    release_date = datetime.strptime(release_date, "%d %b %Y").date()

    # 寫入至資料庫
    print(f"new data: {name}")
    driver = Driver(
        brand=brand,
        model=model,
        name=name,
        version=version,
        importance=importance,
        category=category,
        release_date=release_date,
        download_link=download_link,
        description=description,
        important_information=important_information,
        crawler_info=tr_id,
    )
    session.add(driver)
    session.commit()

# 關閉連線
session.close()

# 等待使用者手動關閉瀏覽器
print("Exiting browser")
# input("Press any key to close the browser...")
browser.quit()
