#!/usr/bin/env python3
from urllib.request import urlopen


if __name__ == '__main__':

    html = urlopen("http://localhost:8080/saiku/rest/saiku/api/license/usercount")
    if html.getcode() == 200:
       print(int(html.read()))
    else:
       print(0)



