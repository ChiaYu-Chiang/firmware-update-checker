# firmware-update-checker

This repository crawler for users to query the updates of each brand's product

## How to install

1. Clone this repository.
* clone with SSH
```cmd
git clone git@github.com:ChiaYu-Chiang/firmware-update-checker.git
```
* clone with HTTPS
```cmd
git clone https://github.com/ChiaYu-Chiang/firmware-update-checker.git
```
2. Enable virtual environment.
```cmd
cd firmware-update-checker\
python -m venv .venv
```
* windows
```cmd
.venv\Scripts\activate
```
* linux
```cmd
source .venv/bin/activate
```
3. Install required packages.
```cmd
pip install -r requirements.txt
```
4. Prepare your webdriver.

## How to use

1. Insert each model you want into models.json 
```json
[
    {
        "brand": "aaa",
        "models": [
            {
                "model": "aaa's model 1",
                "url_model": ""
            },
            {
                "model": "aaa's model 2",
                "url_model": ""
            }
        ]
    },
    {
        "brand": "bbb",
        "models": [
            {
                "model": "bbb's model 1",
                "url_model": ""
            },
            {
                "model": "bbb's model 2",
                "url_model": ""
            }
        ]
    }
]
```
2. Execute program.
```cmd
export line_notify_access_token=your_token
python crawl.py
```
3. Check the database in "brands/databases/".
