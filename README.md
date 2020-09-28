### Spider that crawls all pages on a domain and downloads all files

## Install (on Ubuntu)
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev
python3.8 -m venv ./venv
. venv/bin/activate
pip install -r requirements.txt
```

## Run
# Edit `allowed_domains` and `start_urls` in `spider.py` 
```
scrapy runspider spider.py
```
