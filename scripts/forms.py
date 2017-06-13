import requests
from requests import ConnectionError
import json
import time
from HTMLParser import HTMLParser


class IllegalStateParser(HTMLParser):
    """
    pulls out error codes from data sections
    """
    def __init__(self, data):
        """
        :param data: string 
        """
        HTMLParser.__init__(self)
        self.data = data
        self.results = False

    def handle_data(self, data):
        if self.data in data:
            self.results = True


bamboo_host = "http://localhost:8085"
bitbucket_host = "http://localhost:7990"
r = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

url = str(
    'http://localhost:7990/plugins/servlet/applinks/listApplicationLinks'
)


response = r.get(
    url=url
)

url = 'http://localhost:7990/j_atl_security_check'

form = {
    'j_username': 'bamboo',
    'j_password': 'test',
    '_atl_remember_me': 'on',
    'next': 'http://localhost:7990/plugins/servlet/applinks/listApplicationLinks',
    'submit': 'Log_in'
}

response = r.post(
    url=url,
    data=form
)

parsed = IllegalStateParser(data='Configure Application Links')
parsed.feed(response.text)
if not parsed.results:
    print "Not Application Links Page, raising error"

xsrf_token = response.cookies['atl.xsrf.token']





# print response.text
# print response.status_code

url = str(
    "http://localhost:7990/rest/applinks/3.0/applicationlinkForm/manifest.json?url=" +
    bamboo_host +
    "&_=" +
    str(int(round(time.time() * 1000))))


