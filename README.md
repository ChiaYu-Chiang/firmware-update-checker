# firmware-update-checker

This repository crawler for users to query the updates of each brand's product

## How to install

1. Clone this repository.
* clone with SSH
```shell
git clone git@github.com:ChiaYu-Chiang/firmware-update-checker.git
```
* clone with HTTPS
```shell
git clone https://github.com/ChiaYu-Chiang/firmware-update-checker.git
```
2. Enable virtual environment.
```shell
cd firmware-update-checker\
```
* windows
```shell
python -m venv .venv
.venv\Scripts\activate
```
* linux
```shell
python3 -m venv .venv
source .venv/bin/activate
```
3. Install required packages.
```shell
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
* windows
```shell
set line_notify_access_token=your_token
python crawl.py
```
* linux
```shell
export line_notify_access_token=your_token
python3 crawl.py
```
3. Check the database in "brands/databases/".
