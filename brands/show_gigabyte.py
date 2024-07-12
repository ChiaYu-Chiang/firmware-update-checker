from common_import import *

delay = random.randint(2, 10)


def show_model(model, url_model, date_after=None):
    brand = "gigabyte"

    # 設定 webdriver 參數
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("prefs", {"intl.accept_languages": "en, en_US"})
    options.add_argument("--lang=en-US")
    options.add_argument("headless")
    options.add_argument("window-size=1920,1080")

    # 啟動瀏覽器
    chrome_driver_path = Service("C:/Users/Administrator/Documents/firmware-update-checker/chromedriver")
    browser = webdriver.Chrome(service=chrome_driver_path, options=options)
    wait = WebDriverWait(browser, 30)

    # 訪問網頁
    time.sleep(delay)
    browser.get(url_model)
    
    # 等待firmware資料顯示
    firmware_button = browser.find_element(By.XPATH, '//*[@id="Section-Support"]/div/div[1]/div/ul/ul[1]/li[4]')
    category = firmware_button.get_attribute("data-menu-item")
    browser.execute_script("arguments[0].click();", firmware_button)
    element = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="Section-Support"]/div/div[2]/div[3]/div[4]')
        )
    )
    contents = element.find_elements(By.CLASS_NAME, "ContentLine")
    get_data(brand, category, contents, url_model)
    
    # 等待bios資料顯示
    bios_button = browser.find_element(By.XPATH, '//*[@id="Section-Support"]/div/div[1]/div/ul/ul[1]/li[2]')
    category = bios_button.get_attribute("data-menu-item")
    browser.execute_script("arguments[0].click();", bios_button)
    element = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="Section-Support"]/div/div[2]/div[3]/div[2]')
        )
    )
    contents = element.find_elements(By.CLASS_NAME, "ContentLine")
    get_data(brand, category, contents, url_model)

    # 等待使用者手動關閉瀏覽器
    # input("Press any key to close the browser...")
    browser.quit()
    
    
def get_data(brand, category, contents, url_model):
    # 創建 Session 實例
    session = Session()

    # 遍歷每組資料
    for content in contents:
        # 取得資料
        title = content.find_element(
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
        release_date = datetime.strptime(release_date, "%b %d, %Y").date()

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
                download_link=download_link,
                # description=description,
                # important_information=important_information,
                # crawler_info=crawler_info,
                model_link=url_model
            )
            session.add(driver)
            session.commit()
        else:
            print(f"old data: {title}, released_date: {release_date}")

    # 關閉連線
    session.close()


if __name__ == "__main__":
    model = "R282-3C2"
    url_model = "https://www.gigabyte.com/us/Enterprise/Rack-Server/R282-3C2-rev-100#Support"
    date_after = datetime.strptime("2020-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
