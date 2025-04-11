# SSO頁面登入步驟尚未自動化
from common_import import *
from selenium.common.exceptions import StaleElementReferenceException

delay = random.randint(2, 10)


def show_model(model, url_model, date_after=None):
    brand = "netapp"

    # 設定 webdriver 參數
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("prefs", {"intl.accept_languages": "en, en_US"})
    options.add_argument("--lang=en-US")
    # options.add_argument("headless")
    options.add_argument("window-size=1920,1080")

    # 啟動瀏覽器
    chrome_driver_path = Service("C:/Users/Administrator/Documents/firmware-update-checker/chromedriver")
    browser = webdriver.Chrome(service=chrome_driver_path, options=options)
    wait = WebDriverWait(browser, 30)

    # 訪問網頁
    time.sleep(delay)
    browser.get(url_model)
    input("Press any key to close the browser...")
    # 選擇Platform
    platform_select = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="platforms"]/span/select')))
    platform_select.click()
    option = platform_select.find_element(By.XPATH, './/option[@value="AFF-A200"]')
    option.click()
        
    # 等待元素出現
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="allProductCheck"]',
            )
        )
    )
    type = browser.find_element(
        By.XPATH, '//*[@id="allProductCheck"]/div/div[1]'
    )
    type.click()

    table = browser.find_element(By.XPATH, '//*[@id="ng2-smart-tablefirmware-system-firmware"]/table')
    time.sleep(delay)
    contents = table.find_elements(By.XPATH, 'tbody/tr')

    # 創建 Session 實例
    session = Session()

    # 遍歷每組資料
    for content in contents:

        # 取得資料
        title = browser.find_element(By.XPATH, '//*[@id="content"]/div[3]/app-system-firmware-diagnostics/div/div[5]/div[2]/div[1]').text
        version = content.find_element(By.XPATH, 'td[2]').text
        release_date = content.find_element(By.XPATH, 'td[5]').text
        download_link = content.find_element(By.XPATH, 'td[7]/ng2-smart-table-cell/table-cell-view-mode/div/custom-view-component/app-download-rurl-ender-system/span/a').get_attribute("href")
        description = content.find_element(By.XPATH, 'td[3]').text
        important_information = content.find_element(By.XPATH, 'td[6]/ng2-smart-table-cell/table-cell-view-mode/div/custom-view-component/app-notes-config-render/div/a').get_attribute("href")

        # 資料格式處理
        release_date = datetime.strptime(release_date, "%d-%b-%Y").date()
        # 判斷資料是否已抓過
        record = (
            session.query(Driver)
            .filter_by(brand=brand, model=model, title=title, version=version)
            .first()
        )
        if record:
            print("Data already exist")
            continue

        if release_date > date_after:
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
                download_link=download_link,
                description=description,
                important_information=important_information,
                # crawler_info=crawler_info,
                model_link=url_model,
            )
            session.add(driver)
            session.commit()
        else:
            print(f"old data: {title}, released_date: {release_date}")

    # 關閉連線
    session.close()

    # 等待使用者手動關閉瀏覽器
    # input("Press any key to close the browser...")
    browser.quit()


if __name__ == "__main__":
    model = "AFF-A200"
    url_model = "https://mysupport.netapp.com/site/downloads/firmware/system-firmware-diagnostics"
    date_after = datetime.strptime("2020-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)



