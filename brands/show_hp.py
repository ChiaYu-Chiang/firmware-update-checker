from common_import import *

delay = random.randint(2, 10)


def get_detail_page(link):
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

    time.sleep(delay)
    browser.get(link)

    # 透過 cookie 設定語言為英文
    browser.delete_all_cookies()
    time.sleep(10)
    cookie = {"name": "lang", "value": "en"}
    browser.add_cookie(cookie)
    browser.refresh()

    text_block = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//*[@id="tab-1"]/slot/lightning-formatted-rich-text/span/span',
            )
        )
    )

    try:
        description = text_block.find_element(By.XPATH, "ul[1]/li").text
    except:
        description = text_block.find_element(By.XPATH, "p[3]").text

    try:
        important_information = text_block.find_element(By.XPATH, "ul[2]/li").text
    except:
        try:
            important_information = text_block.find_element(By.XPATH, "p[7]").text
            if important_information == "&nbsp;":
                important_information = None
        except:
            important_information = text_block.find_element(By.XPATH, "ul").text

    browser.quit()
    return [description, important_information]


def use_me(wait, browser, brand, model, baseurl):
    try:
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
        click_test = WebDriverWait(element, 30).until(
            EC.element_to_be_clickable((By.XPATH, "div/div[1]/button/span"))
        )
        time.sleep(delay)
        click_test.click()

        # 點擊選項
        selection = element.find_element(
            By.XPATH,
            "div/div[2]/lightning-base-combobox-item[4]",
        )
        time.sleep(delay)
        selection.click()

        time.sleep(10)
    except:
        pass

    # 定位目標元素
    contents = browser.find_elements(
        By.XPATH,
        "/html/body/div[3]/div[1]/div/div[3]/div/div[2]/div/div/c-dce-product/div/div[2]/lightning-tabset/div/slot/lightning-tab[2]/slot/c-dce-drivers-and-software/c-dce-table/div/div[4]/div/div[1]/div/c-dce-custom-columns-datatable/div[2]/div/div/table/tbody/tr",
    )

    # 創建 Session 實例
    session = Session()

    # 遍歷每組資料
    for content in contents:
        # 取得資料
        title = content.find_element(
            By.XPATH,
            "td[2]/lightning-primitive-cell-factory/span/div/lightning-primitive-custom-cell/c-dce-custom-product-url-cell/div/a",
        ).get_attribute("title")
        version = content.find_element(
            By.XPATH,
            "td[3]/lightning-primitive-cell-factory/span/div/lightning-primitive-custom-cell/div/article/div[1]/span",
        ).text
        importance = content.find_element(
            By.XPATH,
            "th/lightning-primitive-cell-factory/span/div/lightning-primitive-custom-cell/div/div/span",
        ).get_attribute("title")
        category = content.find_element(
            By.XPATH,
            "td[1]/lightning-primitive-cell-factory/span/div/lightning-base-formatted-text",
        ).text
        release_date = content.find_element(
            By.XPATH,
            "td[3]/lightning-primitive-cell-factory/span/div/lightning-primitive-custom-cell/div/article/div[2]/span",
        ).text
        download_link = content.find_element(
            By.XPATH,
            "td[2]/lightning-primitive-cell-factory/span/div/lightning-primitive-custom-cell/c-dce-custom-product-url-cell/div/a",
        ).get_attribute("href")

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

        description = get_detail_page(download_link)[0]
        important_information = get_detail_page(download_link)[1]

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
                # crawler_info=tr_id,
                model_link=baseurl,
            )
            session.add(driver)
            session.commit()
        else:
            print(f"old data: {title}, released_date: {release_date}")

    # 關閉連線
    session.close()


def show_model(model, url_model, date_after=None):
    brand = "hp"

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

    # 訪問網頁
    baseurl = f"https://support.hpe.com/connect/s/product?language=en_US&ismnp={url_model}&tab=driversAndSoftware"
    time.sleep(delay)
    browser.get(baseurl)

    # 透過 cookie 設定語言為英文
    browser.delete_all_cookies()
    time.sleep(10)
    cookie = {"name": "lang", "value": "en"}
    browser.add_cookie(cookie)
    browser.refresh()

    filter_list = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="tab-2"]/slot/c-dce-drivers-and-software/div[1]')
        )
    )
    filter_firmware = filter_list.find_elements(
        By.XPATH, 'c-dce-button-filter/div/button[@title="Firmware"]'
    )
    filter_bios = filter_list.find_elements(
        By.XPATH, 'c-dce-button-filter/div/button[@title="BIOS"]'
    )

    if filter_firmware:
        time.sleep(delay)
        filter_firmware[0].click()
        use_me(wait=wait, browser=browser, brand=brand, model=model, baseurl=baseurl)
    if filter_bios:
        time.sleep(delay)
        filter_bios[0].click()
        use_me(wait=wait, browser=browser, brand=brand, model=model, baseurl=baseurl)

    # 等待使用者手動關閉瀏覽器
    # input("Press any key to close the browser...")
    browser.quit()


if __name__ == "__main__":
    model = "DL380 G7"
    url_model = "0&l5oid=4091412&cep=on&kmpmoid=4091567"
    date_after = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
