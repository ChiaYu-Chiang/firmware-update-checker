# SSO頁面登入步驟尚未自動化
from common_import import *
from selenium.common.exceptions import StaleElementReferenceException

delay = random.randint(2, 10)


def show_model(model, url_model, date_after=None):
    brand = "fortinet"

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
    platform_select = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-panel"]/div/app-downloads-vm/forticare-region-overlay-loading/div[2]/div[1]/div[4]/div[2]/div[2]/select')))
    platform_select.click()
    xen_option = platform_select.find_element(By.XPATH, './/option[@value="Xen"]')
    esxi_option = platform_select.find_element(By.XPATH, './/option[@value="VMWare ESXi"]')
    options = [xen_option, esxi_option]

    for option in options:
        option.click()
        
        # 等待元素出現
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="ngb-nav-0-panel"]/ag-grid-angular/div/div[2]/div[2]/div[3]/div[2]/div/div',
                )
            )
        )
        blocks = browser.find_elements(
            By.XPATH, '//*[@id="ngb-nav-0-panel"]/ag-grid-angular/div/div[2]/div[2]/div[3]/div[2]/div/div/div'
        )
        
        # 展開
        for block in blocks:
            block.click()

        contents = browser.find_elements(
            By.XPATH, '//*[@id="ngb-nav-0-panel"]/ag-grid-angular/div/div[2]/div[2]/div[3]/div[4]/div/app-vm-detail-cell-renderer/ag-grid-angular/div/div[2]/div[2]/div[3]/div[2]/div/div/div'
        )

        # 創建 Session 實例
        session = Session()

        # 遍歷每組資料
        for content in contents:
            titlefile = content.find_element(By.XPATH, "div[1]").text
            parts = titlefile.split('\n')

            # 取得資料
            title = parts[0].strip()
            release_date = content.find_element(By.XPATH, "div[3]").text
            description = parts[1].strip()
            pattern = r'v(\d+\.\d+\.\d+)\.'
            match = re.search(pattern, description)
            version = match.group(1)
            crawler_info = content.get_attribute('comp-id')
            category = option.text.strip()

            # 資料格式處理
            release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
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

            if release_date > date_after:
                # 寫入至資料庫
                print(f"new data: {title}")
                driver = Driver(
                    brand=brand,
                    model=model,
                    title=title,
                    version=version,
                    # importance=importance,
                    category=category,
                    release_date=release_date,
                    download_link=url_model,
                    description=description,
                    # important_information=important_information,
                    crawler_info=crawler_info,
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
    model = "60E"
    url_model = "https://support.fortinet.com/support/#/downloads/vm"
    date_after = datetime.strptime("2020-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
