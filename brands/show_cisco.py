from common_import import *

delay = random.randint(2, 10)


def show_model(model, url_model, date_after=None):
    brand = "cisco"

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
    for content in contents:
        # 取得資料
        title = content.find_element(By.XPATH, "div/div[1]/div[1]/div/span").text
        version = browser.find_element(
            By.XPATH, '//*[@id="release-version-title"]'
        ).text.split('\n')[0].strip()
        release_date = content.find_element(By.XPATH, "div/div[2]").text
        download_link = url_model
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
                # description=description,
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
    model = "Nexus N9K-C9372PX"
    url_model = (
        "https://software.cisco.com/download/home/286279782/type/282088129/release"
    )
    date_after = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
