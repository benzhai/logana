#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup

headers = {
"user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
}
proxies ={
    "http":'http://122.193.14.102:80',
    "https":"http://120.203.18.33:8123"
}

r = requests.get('http://www.ip.cn',headers=headers,proxies=proxies)
content = r.text

ip=re.search(r'code.(.*?)..code', content)

print (ip.group(1))