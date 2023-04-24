from common_import import *

delay = random.randint(2, 5)


def show_model(model, url_model, date_after=None):
    brand = "qnap"

    # 設定 webdriver 參數
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("headless")
    options.add_argument("window-size=1920,1080")

    # 啟動瀏覽器
    chrome_driver_path = Service("../chromedriver")
    browser = webdriver.Chrome(service=chrome_driver_path, options=options)
    wait = WebDriverWait(browser, 30)

    # 訪問網頁
    baseurl = f"https://www.qnap.com/en-us/download?model={url_model}&category=firmware"
    time.sleep(delay)
    browser.get(baseurl)

    # 等待元素出現
    element = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="download_result"]/div[3]/table/tbody',
            )
        )
    )

    # 定位目標元素
    contents = element.find_elements(By.XPATH, "tr")

    # 創建 Session 實例
    session = Session()

    # 遍歷每組資料
    for content in contents:
        # 取得資料
        title = content.find_element(By.XPATH, "td[1]/div").text
        version = content.find_element(By.XPATH, "td[2]").text
        release_date = content.find_element(By.XPATH, "td[3]").text
        download_link = content.find_element(
            By.XPATH, "td[4]/ul/li[1]/a"
        ).get_attribute("href")
        description = content.find_element(By.XPATH, "td[5]/a").get_attribute(
            "data-note"
        )

        # 資料格式處理
        release_date = datetime.strptime(release_date, "%Y-%m-%d").date()

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
                # category=category,
                release_date=release_date,
                download_link=download_link,
                description=description,
                # important_information=important_information,
                # crawler_info=crawler_info,
                model_link=baseurl,
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
    model = "TS-269L"
    url_model = "ts-269l"
    date_after = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
