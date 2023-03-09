from common_import import *


def show_model(model, url_model):
    brand = "juniper"

    # 設定 webdriver 參數
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("headless")
    options.add_argument("window-size=1920,1080")

    # 啟動瀏覽器
    browser = webdriver.Chrome(options=options)
    wait = WebDriverWait(browser, 30)

    # 訪問網頁
    baseurl = "https://support.juniper.net/support/downloads/?p={}".format(url_model)
    browser.get(baseurl)

    # 點擊展開按鈕
    button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="downloads-info"]/section/section[1]/div[2]/a')
        )
    )
    button.click()

    # 等待元素出現
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                '//*[@id="downloads-info"]/section/section/div[2]/mat-table',
            )
        )
    )
    sections = browser.find_elements(
        By.XPATH, '//*[@id="downloads-info"]/section/section'
    )

    for section in sections:
        try:
            section_title = section.find_element(By.XPATH, "div[1]/h2").text
        except:
            section_title = None
        if section_title not in [
            "Application Package",
            "Install Package",
            "Install Media",
            "Tools",
        ]:
            continue
        else:
            # 定位目標元素
            contents = section.find_elements(By.XPATH, "div[2]/mat-table/mat-row")

            # 創建 Session 實例
            session = Session()

            # 遍歷每組資料
            for content in contents:
                # 取得資料
                title = content.find_element(By.XPATH, "mat-cell[1]/span").text
                version = content.find_element(By.XPATH, "mat-cell[2]").text
                release_date = content.find_element(By.XPATH, "mat-cell[3]").text
                download_link = content.find_element(
                    By.XPATH, "mat-cell[4]/a[1]"
                ).get_attribute("href")

                # 資料格式處理
                release_date = datetime.strptime(release_date, "%d %b %Y").date()

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
                    # importance=importance,
                    category=section_title,
                    release_date=release_date,
                    download_link=download_link,
                    # description=description,
                    # important_information=important_information,
                    # crawler_info=crawler_info,
                    model_link=baseurl,
                )
                session.add(driver)
                session.commit()

            # 關閉連線
            session.close()

    # 等待使用者手動關閉瀏覽器
    # input("Press any key to close the browser...")
    browser.quit()


if __name__ == "__main__":
    model = "SRX4100"
    url_model = "srx4100"
    show_model(model, url_model)
