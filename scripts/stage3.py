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

url = str(
    'http://localhost:7990/plugins/servlet/applinks/listApplicationLinks'
)

r.get(
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

# print response.text
bamboo_server = open('bamboo_server').read()

url = "http://localhost:7990/rest/applinks/3.0/applinks/" + bamboo_server + "?data=configUrl&data=iconUri"

form = {
    'id': str(r),
    'statusLoaded': True,
    'status': {
        'link': {
            'id': str(r),
            'name': "Atlassian+Bamboo",
            'displayUrl': bamboo_host,
            'rpcUrl': bamboo_host,
            'type': 'bamboo'
        },
        'working': False,
        'localAuthentication': {
            'incoming': {
                'enabled': False,
                'twoLoEnabled': False,
                'twoLoImpersonationEnabled': False
            }
        },
        'remoteAuthentication': {
            'incoming': {
                'enabled': False,
                'twoLoEnabled': False,
                'twoLoImpersonationEnabled': False
            }
        },
        'error': {
            'category': "DISABLED",
            'type': 'DISABLED'
        }
    },
    'name': "Atlassian+Bamboo",
    'displayUrl': bamboo_host,
    'rpcUrl': bamboo_host,
    'type': 'bamboo',
    'system': False,
    'primary': True,
    'data': {
        'configUrl': bamboo_host + '/plugins/servlet/applinks/listApplicationLinks',
        'iconUri': bamboo_host + '/s/126369268/2d88633/1/5.2.6/_/download/resources/com.atlassian.applinks.applinks-plugin:applinks-images/images/config/logos/128x128/128bamboo.png'
    }
}

modified_headers = headers

modified_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
modified_headers['content-Type'] = 'application/json; charset=utf-8'
modified_headers['X-Requested-With'] = 'XMLHttpRequest'

r.put(
    url=url,
    headers=modified_headers,
    cookies=cookies,
    data=json.dumps(form)
)

url = 'http://localhost:7990/rest/applinks/3.0/status/' + bamboo_server + '/oauth'

form = {
    'incoming': {
        'enabled': True,
        'twoLoEnabled': True,
        'twoLoImpersonationEnabled': False
    },
    'outgoing': {
        'enabled': True,
        'twoLoEnabled': True,
        'twoLoImpersonationEnabled': False
    }
}

response = r.put(
    url=url,
    headers=modified_headers,
    cookies=cookies,
    data=json.dumps(form)
)

if not int(response.status_code) == 204:
    print response.text
    print response.status_code
    print "Unexpected server response, applications not linked"
    raise Exception

print "Initial Bamboo->Bitbucket Link Configured"

