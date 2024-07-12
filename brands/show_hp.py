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
    chrome_driver_path = Service("C:/Users/Administrator/Documents/firmware-update-checker/chromedriver")
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
                '//*[@id="dceContent"]/div/div[2]/div/div/c-dce-software-collection/div[last()]/div[2]/div[2]/c-dce-software-collection-tabs/div/c-dce-tabset/div/div[2]/slot/c-dce-tab[1]/slot/lightning-formatted-rich-text/span'
            )
        )
    )

    try:
        description = text_block.find_element(By.XPATH, "p[3]").text
    except:
        description = None

    try:
        important_information = text_block.find_element(By.XPATH, "p[6]").text
    except:
        important_information = None
    
    browser.quit()
    return [description, important_information]


def use_me(wait, browser, brand, model, baseurl):
    try:
        # 等待元素出現
        element = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="tab-3"]/slot/c-dce-drivers-and-software/c-dce-table/div/div[4]/div/div[2]/c-dce-pager/nav/div/lightning-combobox/div/div/lightning-base-combobox',
                )
            )
        )

        # 點擊選單
        click_test = WebDriverWait(element, 30).until(
            EC.element_to_be_clickable((By.XPATH, "div/div/div[1]/button/span"))
        )
        time.sleep(delay)
        click_test.click()

        # 點擊選項
        selection = element.find_element(
            By.XPATH,
            "div/div/div[2]/lightning-base-combobox-item[4]",
        )
        time.sleep(delay)
        selection.click()

        time.sleep(10)
    except:
        pass

    # 定位目標元素
    contents = browser.find_elements(
        By.XPATH,
        "//*[@id='tab-3']/slot/c-dce-drivers-and-software/c-dce-table/div/div[4]/div/div[1]/div/c-dce-custom-columns-datatable/div[2]/div/div/table/tbody/tr",
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
        if importance == "Recommended":
            importance = "RECOMMENDED"
        elif importance == "Optional":
            importance = "OPTIONAL"
        elif importance == "Critical":
            importance = "CRITICAL"
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
    chrome_driver_path = Service("C:/Users/Administrator/Documents/firmware-update-checker/chromedriver")
    browser = webdriver.Chrome(service=chrome_driver_path, options=options)
    wait = WebDriverWait(browser, 30)

    # 訪問網頁
    time.sleep(delay)
    browser.get(url_model)

    # 透過 cookie 設定語言為英文
    browser.delete_all_cookies()
    time.sleep(10)
    cookie = {"name": "lang", "value": "en"}
    browser.add_cookie(cookie)
    browser.refresh()

    filter_list = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="tab-3"]/slot/c-dce-drivers-and-software/div[1]')
        )
    )
    filter_firmware = filter_list.find_elements(
        By.XPATH, 'c-dce-button-filter/div/button[@title="Firmware"]'
    )[0]
    filter_bios = filter_list.find_elements(
        By.XPATH, 'c-dce-button-filter/div/button[@title="BIOS"]'
    )[0]
    if filter_firmware:
        time.sleep(delay)
        browser.execute_script("arguments[0].click();", filter_firmware)
        use_me(wait=wait, browser=browser, brand=brand, model=model, baseurl=url_model)
    if filter_bios:
        time.sleep(delay)
        browser.execute_script("arguments[0].click();", filter_bios)
        use_me(wait=wait, browser=browser, brand=brand, model=model, baseurl=url_model)

    # 等待使用者手動關閉瀏覽器
    # input("Press any key to close the browser...")
    browser.quit()


if __name__ == "__main__":
    model = "DL380 G11"
    url_model = "https://support.hpe.com/connect/s/product?language=en_US&cep=on&kmpmoid=1014696069&tab=driversAndSoftware"
    date_after = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
