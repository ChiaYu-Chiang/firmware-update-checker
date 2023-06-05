# firmware-update-checker

This repository crawler for users to query the updates of each brand's product. 
<br>The update information will be displayed on the web page. 

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
python -m venv .venv
source .venv/bin/activate
```
3. Install required packages.
```shell
pip install -r requirements.txt
```
4. Prepare your webdriver.

## How to use

1. Visit website.
* <http://127.0.0.1:5001/add_model>
* input the target of crawler and submit to database
2. Execute program.
* windows
```shell
# if use reverse proxy
# set HOST=127.0.0.1
set line_notify_access_token=your_token
python crawl.py
```
* linux
```shell
# if use reverse proxy
# export HOST=127.0.0.1
export line_notify_access_token=your_token
python crawl.py
```

3. Start up the web server.
```shell
python run_waitress.py
```
4. Visit website.
* <http://127.0.0.1:5001>

