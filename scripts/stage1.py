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


def parse_string_dictionary(dictionary):
    """
    Hand over a string that should be a dictionary, and this should turn it into a dictionary
    :param dictionary: 
    :return: 
    """
    resulting_dictionary = {}
    items = dictionary.strip('{').strip('}').split(',')
    for item in items:
        split_item = item.split(":")
        name = split_item[0].strip('"')
        try:
            value = split_item[1].strip('"')
        except IndexError:
            value = ""
        resulting_dictionary[name] = value

    return resulting_dictionary


bamboo_host = "http://10.0.2.15:8085"
bitbucket_host = "http://10.0.2.15:7990"
r = requests.session()

time.sleep(2)

headers = {
    'Host': 'localhost:7990',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

url = str(
    'http://localhost:7990/plugins/servlet/applinks/listApplicationLinks'
)

response = r.get(
    url=url,
    headers=headers
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
    headers=headers,
    data=form
)

parsed = IllegalStateParser(data='Configure Application Links')
parsed.feed(response.text)
if not parsed.results:
    url = str(
        'http://localhost:7990/plugins/servlet/applinks/listApplicationLinks'
    )
    response = r.get(
        url=url
    )
    parsed.feed(response.text)
    if not parsed.results:
        print response.text
        print response.status_code
        print "Not Application Links Page, raising error"
        raise Exception

xsrf_token = response.cookies['atl.xsrf.token']

cookies = {
    'atl.xsrf.token': xsrf_token
}

url = str(
    "http://localhost:7990/rest/applinks/3.0/applicationlinkForm/manifest.json?url=" +
    bamboo_host +
    "&_=" +
    str(int(round(time.time() * 1000))))

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies
)




results = parse_string_dictionary(response.text)


x = 1

for name, value in results.iteritems():
    if name == "name":
        if value == "Atlassian+Bamboo":
            x = 0
            break

if x == 1:
    print response.text
    print response.status_code
    print "Atlassian+Bamboo was not linked"
    raise Exception

for name, value in results.iteritems():
    if name == "id":
        server_id = value

url = "http://localhost:7990/rest/applinks/3.0/applicationlink"

form = {
    'id': server_id,
    'name': 'Atlassian+Bamboo',
    'rpcUrl': bamboo_host,
    'displayUrl': bamboo_host,
    'typeId': 'bamboo'
}

modified_headers = headers

modified_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
modified_headers['content-Type'] = 'application/json; charset=utf-8'
modified_headers['X-Requested-With'] = 'XMLHttpRequest'


response = r.put(
    url=url,
    headers=modified_headers,
    data=json.dumps(form),
)

print "link is complete on Bitbucket"

with open('bamboo_server', 'w+') as f:

    f.write(server_id)
    f.truncate()
