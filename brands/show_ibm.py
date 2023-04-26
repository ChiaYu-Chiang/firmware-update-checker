from common_import import *

delay = random.randint(2, 10)


def show_model(model, url_model, date_after=None):
    brand = "ibm"
    url_model_brocade = url_model + "_brocade"

    # 設定 webdriver 參數
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("prefs", {"intl.accept_languages": "en, en_US"})
    options.add_argument("--lang=en-US")
    options.add_argument("headless")
    options.add_argument("window-size=1920,1080")

    # 啟動瀏覽器
    chrome_driver_path = Service("../chromedriver")
    browser = webdriver.Chrome(service=chrome_driver_path, options=options)
    wait = WebDriverWait(browser, 30)

    baseurl = (
        f"https://www.ibm.com/support/fixcentral/{url_model}&&platform=All&function=all"
    )
    baseurl_brocade = f"https://www.ibm.com/support/fixcentral/{url_model_brocade}&&platform=All&function=all"
    urls = [baseurl, baseurl_brocade]

    for url in urls:
        time.sleep(delay)
        # 訪問網頁
        browser.get(url)

        # 選擇 Firmware Update
        filter_area = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="ibm-content-main"]/div[1]/div[2]/div[3]/div')
            )
        )
        try:
            filter = WebDriverWait(filter_area, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "div/form/div[2]/div[1]/div/p[7]")
                )
            )
            time.sleep(delay)
            filter.click()
            submit = filter_area.find_element(By.XPATH, "div/form/p[5]/button")
            time.sleep(delay)
            submit.click()
        except:
            print("no firmware update found")
            pass

        # 等待元素消失
        wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//*[@id="ibm-overlaywidget-fc-filter-overlay"]')
            )
        )

        # 等待元素出現
        element = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div[4]/main/div/div/div/div/div[1]/div[1]/div/div[2]/form[2]/div/div/div",
                )
            )
        )

        # 定位目標元素
        contents = element.find_elements(By.XPATH, "div/div/table/tbody/tr")

        # 創建 Session 實例
        session = Session()

        # 遍歷每組資料
        for content in contents:
            element = content.find_element(
                By.XPATH,
                "td[2]/div[1]",
            )
            browser.execute_script("arguments[0].style.display='block'", element)

            # 取得資料
            title = content.find_element(By.XPATH, "td[2]/p").text.split("\n")[-1]
            version = (
                element.find_element(By.XPATH, "p[2]").text.split(":", 1)[-1].strip()
            )
            importance = (
                element.find_element(By.XPATH, "p[3]")
                .text.split(":", 1)[-1]
                .replace("&nbsp;", "")
                .strip()
            )
            category = (
                element.find_element(By.XPATH, "p[4]").text.split(":", 1)[-1].strip()
            )
            release_date = content.find_element(By.XPATH, "td[3]").text
            download_link = content.find_element(By.XPATH, "td[2]/p/a").get_attribute(
                "href"
            )
            description = (
                element.find_element(By.XPATH, "p[5]").text.split(":", 1)[-1].strip()
            )
            important_information = content.find_element(By.XPATH, "td[2]/p/a").text

            # 資料格式處理
            importance = None if importance == "" else importance
            release_date = datetime.strptime(release_date, "%Y/%m/%d").date()
            if url == baseurl:
                baseurl = baseurl
            else:
                baseurl = baseurl_brocade

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
                    importance=importance,
                    category=category,
                    release_date=release_date,
                    download_link=download_link,
                    description=description,
                    important_information=important_information,
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
    model = "x3250M3"
    url_model = (
        "systemx/selectFixes?parent=System%20x3250%20M3&product=ibm/systemx/4252"
    )
    date_after = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
