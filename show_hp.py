from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from database import Session, Driver

brand = "hp"
model = "DL380 G7"

# 設定 webdriver 參數
options = Options()
# options.add_argument("headless")
options.add_argument("window-size=1920,1080")

# 啟動瀏覽器
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)

# 訪問網頁
browser.get(
    "https://support.hpe.com/connect/s/product?language=en_US&kmpmoid=4091567&tab=driversAndSoftware&driversAndSoftwareFilter=8000029"
)

# 等待元素出現
element = wait.until(
    EC.visibility_of_element_located(
        (
            By.XPATH,
            '//*[@id="tab-2"]/slot/c-dce-drivers-and-software/c-dce-table/div/div[4]/div/div[2]/c-dce-pager/nav/div/lightning-combobox/div/lightning-base-combobox',
        )
    )
)

# 點擊選單
click_test = element.find_element(By.XPATH, "div/div[1]/button/span")
click_test.click()

# 點擊選項
selection = element.find_element(
    By.XPATH,
    "div/div[2]/lightning-base-combobox-item[4]",
)
selection.click()

# 創建 Session 實例
session = Session()

# 爬蟲階段

# 關閉連線
session.close()

# 等待使用者手動關閉瀏覽器
print("Exiting browser")
input("Press any key to close the browser...")
browser.quit()
