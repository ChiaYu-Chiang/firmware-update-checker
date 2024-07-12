from common_import import *

delay = random.randint(2, 10)


def show_model(model, url_model, date_after=None):
    brand = "dell"

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
    cookie = {"name": "lwp", "value": "c=us&l=en&cs=04&s=bsd"}
    browser.add_cookie(cookie)
    browser.refresh()
    time.sleep(2)

    os_selector = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="driverFilter"]/div[2]/label')
        )
    ).get_attribute("for")
    if os_selector != "no-os":
        # 找到下拉式選單
        element = wait.until(EC.element_to_be_clickable((By.ID, "operating-system")))
        try:
            time.sleep(delay)
            # 選擇 option value="NAA" 的選項
            select = Select(element)
            select.select_by_value("NAA")
        except:
            pass

    filter_button = wait.until(EC.element_to_be_clickable((By.ID, "ddl-dwldtype-btn")))
    time.sleep(delay)
    browser.execute_script("arguments[0].click();", filter_button)
    time.sleep(2)
    try:
        # 勾選 BIOS 和韌體的 checkbox
        filter_BIOS = browser.find_element(By.XPATH, '//*[@id="ddl-dwldtype_BIOS"]')
        filter_FRMW = browser.find_element(By.XPATH, '//*[@id="ddl-dwldtype_FRMW"]')
        browser.execute_script("arguments[0].click();", filter_BIOS)
        browser.execute_script("arguments[0].click();", filter_FRMW)
    except:
        pass
    # 點擊下載類型的按鈕以收起選項
    time.sleep(delay)
    browser.execute_script("arguments[0].click();", filter_button)

    try:
        # 等待按鈕元素出現
        show_all_button = wait.until(
            EC.element_to_be_clickable((By.ID, "paginationRow"))
        )

        time.sleep(delay)
        # 點擊按鈕
        browser.execute_script("arguments[0].click();", show_all_button)
    except:
        None

    # 定位按鈕元素
    buttons = browser.find_elements(By.NAME, "btnDriverListToggle")

    # 創建 Session 實例
    session = Session()

    # 點擊每個按鈕
    for button in buttons:
        tr_id = button.find_element(By.XPATH, "../..").get_attribute("id").split("_")[1]

        # 判斷資料是否已抓過
        record = (
            session.query(Driver)
            .filter_by(brand=brand, model=model, crawler_info=tr_id)
            .first()
        )
        if record:
            if record.crawler_info == tr_id:
                print("Data already exist")
                continue

        # 定位節點
        tableRow_point = button.find_element(By.XPATH, f'//tr[@id="tableRow_{tr_id}"]')
        title = tableRow_point.find_element(By.XPATH, "td[2]/div/div[2]").text
        release_date = tableRow_point.find_element(By.XPATH, "td[5]").text

        # 資料格式處理
        release_date = datetime.strptime(release_date, "%d %b %Y").date()

        if release_date > date_after:
            time.sleep(delay)
            # 點擊按鈕
            # button.click()
            browser.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)
            browser.execute_script("arguments[0].click();", button)

            # 等待資料顯示出來
            wait.until(EC.presence_of_element_located((By.ID, f"child_{tr_id}")))
            child_point = button.find_element(
                By.XPATH, f'//tr[@id="child_{tr_id}"]/td[2]/section'
            )

            # 取得資料
            version = child_point.find_element(By.XPATH, "div[5]/div[1]/p").text
            importance = tableRow_point.find_element(By.XPATH, "td[3]/span").text
            category = tableRow_point.find_element(By.XPATH, "td[4]").text
            download_link = tableRow_point.find_element(
                By.XPATH, "td[6]/div/a[2]"
            ).get_attribute("href")
            description = child_point.find_element(By.XPATH, "div[7]/p").text
            try:
                imp_info = child_point.find_element(By.XPATH, "div[8]/p")
                imp_info_innerHTML = imp_info.get_attribute("innerHTML").replace(
                    "<br>", "\n"
                )
                important_information = (
                    re.sub(r"<.*?>", "", imp_info_innerHTML)
                    .replace("&nbsp;&nbsp;閱讀更多", "")
                    .strip()
                )
                # 若為 loading 則等待後再次執行
                if important_information == " Loading...":
                    print("because loading")
                    time.sleep(delay)
                    imp_info = child_point.find_element(By.XPATH, "div[8]/p[2]")
                    imp_info_innerHTML = imp_info.get_attribute("innerHTML").replace(
                        "<br>", "\n"
                    )
                    important_information = (
                        re.sub(r"<.*?>", "", imp_info_innerHTML)
                        .replace("&nbsp;&nbsp;閱讀更多", "")
                        .strip()
                    )
            except NoSuchElementException:
                important_information = None

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
                crawler_info=tr_id,
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
    model = "R640"
    url_model = "https://www.dell.com/support/home/en-us/product-support/product/poweredge-r640/drivers"
    date_after = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)
