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


url = 'http://localhost:8085/userlogin!doDefault.action'

response = r.get(
    url=url
)

cookies = {}

cookies['JSESSIONID'] = response.cookies['JSESSIONID']
cookies['atl.xsrf.token'] = response.cookies['atl.xsrf.token']

url = 'http://localhost:8085/userlogin.action'

form = {
    'os_destination': '/start.action',
    'os_username': 'bamboo',
    'os_password': 'test',
    'checkBoxFields': 'os_cookie',
    'save': 'Log+in',
    'atl_token': cookies['atl.xsrf.token']
}

r.post(
    url=url,
    headers=headers,
    cookies=cookies,
    data=form
)

url = 'http://localhost:8085/plugins/servlet/applinks/listApplicationLinks'

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies
)

results = IllegalStateParser(data='Configure Application Links')
results.feed(response.text)
if not results.results:
    print response.text
    print response.status_code
    print "not at Configure Application Links page"
    raise Exception

cookies['bamboo.dash.display.toggles'] = 'buildQueueActions-actions-queueControl'

url = str(
    "http://10.0.2.15:8085/rest/applinks/3.0/applicationlinkForm/manifest.json?url=" +
    bitbucket_host +
    "&_=" +
    str(int(round(time.time() * 1000))))

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies,
)

parsed_dictionary = parse_string_dictionary(response.text)

for name, value in parsed_dictionary.iteritems():
    if name == "id":
        server_id = value
        break
if not server_id:
    for name, value in parsed_dictionary.iteritems():
        print name, value
    print parsed_dictionary
    print response.text
    print response.status_code
    print "No server ID provided"
    raise Exception


url = "http://localhost:8085/rest/api/latest/server?_=" + str(int(round(time.time() * 1000)))

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies
)

parsed = IllegalStateParser(data='RUNNING')
parsed.feed(response.text)
if not parsed.results:
    print response.text
    print response.status_code
    print "Results unexpected"
    raise Exception

url = 'http://localhost:8085/rest/applinks/3.0/applicationlink'

form = {
    'id': server_id,
    'name': 'Bitbucket',
    'rpcUrl': 'http://10.0.2.15:7990',
    'displayUrl': 'http://192.168.253.52:7990',
    'typeId': "stash"
}

modified_headers = headers

modified_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
modified_headers['content-Type'] = 'application/json; charset=utf-8'
modified_headers['X-Requested-With'] = 'XMLHttpRequest'

response = r.put(
    url=url,
    headers=modified_headers,
    cookies=cookies,
    data=json.dumps(form)
)

print "link is complete on Bamboo"

with open('bitbucket_server', 'r+') as f:
    f.write(server_id)
    f.truncate()
