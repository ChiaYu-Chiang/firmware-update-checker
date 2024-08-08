from common_import import *

delay = random.randint(2, 10)

def insert_data(session, brand, model, title, version, importance=None, category=None, release_date=None, download_link=None, description=None, important_information=None, crawler_info=None):
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
        crawler_info=crawler_info
    )
    session.add(driver)
    session.commit()
    
# def insert_data(session, brand, model, title, version, importance=None, category=None, release_date=None, download_link=None, description=None, important_information=None, crawler_info=None):
#     driver = [
#         brand,
#         model,
#         title,
#         version,
#         importance,
#         category,
#         release_date,
#         download_link,
#         description,
#         important_information,
#         crawler_info
#     ]
#     print(driver)

def identify_tr_type(tr_element):
    # 檢查是否包含多個<p>元素
    p_elements = tr_element.find_elements(By.TAG_NAME, "p")
    text_content = tr_element.text
    has_dell_hardware = "Dell hardware only" in text_content
    has_update_available = "Update available" in text_content
    
    if len(p_elements) > 1:
        if has_dell_hardware and has_update_available:
            return "Type 1"
        elif has_update_available:
            return "Type 3"
        else:
            return "Type 1"
    
    # 檢查是否包含"Dell hardware only"
    if "Dell hardware only" in tr_element.text:
        return "Type 2"
    
    # 檢查是否包含"Update available"
    if "Update available" in tr_element.text:
        return "Type 3"
    
    # 如果只包含一個版本號
    if text_content.strip().count('.') >= 2 and len(tr_element.find_elements(By.TAG_NAME, "a")) == 0:
        return "Type 4"
    
    return "Unknown Type"

def show_model(model, url_model, date_after=None):
    brand = "citrix"
    
    # 設定 webdriver 參數
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("prefs", {"intl.accept_languages": "en, en_US"})
    options.add_argument("--lang=en-US")
    options.add_argument("headless")
    options.add_argument("windows-size=1920,1080")
    
    # 啟動瀏覽器
    chrome_driver_path = Service("C:/Users/Administrator/Documents/firmware-update-checker/chromedriver")
    browser = webdriver.Chrome(service=chrome_driver_path, options=options)
    wait = WebDriverWait(browser, 30)
    
    # 訪問網頁
    browser.get(url_model)
    
    # 等待元素出現
    element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/article[2]/div/div/div/div/div[7]/div/div/div[2]/span/div/table[1]')))
    
    release_date = browser.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/article[2]/div/div/div/div/div[6]/div/div/div[2]/span/span').text
    # 資料格式處理
    release_date = datetime.strptime(release_date, "%d/%b/%Y")
    
    # 定位目標元素
    contents = element.find_elements(By.XPATH, "tbody/tr[position()>1]")
    
    session = Session()
    
    # 遍歷每組資料
    for content in contents:
        if model == "Citrix Hypervisor 8.2":
            version = content.find_element(By.XPATH, "td[3]")
        elif model == "XenServer 8":
            version = content.find_element(By.XPATH, "td[4]")
        else:
            print("unsupported model")
        
        title = content.find_element(By.XPATH, "td[1]").text
        category = content.find_element(By.XPATH, "td[2]").text
        
        match identify_tr_type(version):
            case "Type 1":
                versions = version.find_elements(By.XPATH, "ul/li/a")
                for version_content in versions:
                    version = version_content.text.strip()
                    download_link = version_content.get_attribute("href")
                    # 判斷資料是否已抓過
                    record = (session.query(Driver).filter_by(brand=brand, model=model, title=title, version=version).first())
                    if record:
                        print("Data already exist")
                        continue
                    # 寫入至資料庫
                    print(f"new data: {title}")
                    insert_data(session, brand, model, title, version, category=category, release_date=release_date, download_link=download_link)
                
            case "Type 2":
                version_content = version.find_element(By.XPATH, "a")
                version = version_content.text.strip()
                download_link = version_content.get_attribute("href")
                # 判斷資料是否已抓過
                record = (session.query(Driver).filter_by(brand=brand, model=model, title=title, version=version).first())
                if record:
                    print("Data already exist")
                    continue
                # 寫入至資料庫
                print(f"new data: {title}")
                insert_data(session, brand, model, title, version, category=category, release_date=release_date, download_link=download_link)
                
            case "Type 3":
                try:
                    version_text = version.find_element(By.XPATH, "p")
                    if "Update available" in version_text.text:
                        version_content = version_text.find_element(By.XPATH, "a")
                    else:
                        version_content = version.find_element(By.XPATH, "p[2]/a")
                except:
                    version_content = version.find_element(By.XPATH, "a")
                version = version_content.text.strip()
                download_link = version_content.get_attribute("href")
                # 判斷資料是否已抓過
                record = (session.query(Driver).filter_by(brand=brand, model=model, title=title, version=version).first())
                if record:
                    print("Data already exist")
                    continue
                # 寫入至資料庫
                print(f"new data: {title}")
                insert_data(session, brand, model, title, version, category=category, release_date=release_date, download_link=download_link)
            case "Type 4":
                version = version.text.strip()
                # 判斷資料是否已抓過
                record = (session.query(Driver).filter_by(brand=brand, model=model, title=title, version=version).first())
                if record:
                    print("Data already exist")
                    continue
                # 寫入至資料庫
                print(f"new data: {title}")
                insert_data(session, brand, model, title, version, category=category)
            case "Unknown Type":
                pass
        
    # 關閉連線
    session.close()
    
    browser.quit()
    
    
if __name__ == "__main__":
    model = "XenServer 8"
    url_model = "https://support.citrix.com/s/article/CTX257603-available-driver-versions-for-xenserver-and-citrix-hypervisor?language=en_US"
    date_after = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
    show_model(model, url_model, date_after)