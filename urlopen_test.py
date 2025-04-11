import requests
from requests.exceptions import HTTPError

try:
    model_link = "https://software.cisco.com/download/home/286279793/type/282088129/release"
    response = requests.get(model_link, allow_redirects=True)
    
    if response.status_code == 302:
        # 如果有302重定向，進一步處理或略過
        print("Encountered a 302 redirect")
    else:
        print("Access successful")

except HTTPError as e:
    if e.response.status_code != 302:
        print("Please check URL")
except Exception as e:
    print("Something went wrong:", str(e))
