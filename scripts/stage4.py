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
    'Host': "localhost:8085",
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

response = r.post(
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

bitbucket_server = open('bitbucket_server').read()
bamboo_server = open('bamboo_server').read()

url = 'http://localhost:7990/j_atl_security_check'

next_url = 'http://localhost:7990/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
            bamboo_server + \
            '?uiposition=remote&hostUrl=http%3A%2F%2F10.0.2.15%3A8085&outgoing2LOEnabled=false&outgoing2LOiEnabled=false&oauth-outgoing-enabled=true'


form = {
    'j_username': 'bamboo',
    'j_password': 'test',
    '_atl_remember_me': 'on',
    'next': next_url,
    'submit': 'Log_in',
    'permission': 'ADMIN'
}

response = r.post(
    url=url,
    headers=headers,
    data=form
)

if not int(response.status_code) == 200:
    print response.text
    print response.status_code
    print "unexpected response"
    raise Exception

url = 'http://localhost:8085/userlogin.action'

form = {
    'os_destination': '/start.action',
    'os_username': 'bamboo',
    'os_password': 'test',
    'checkBoxFields': 'os_cookie',
    'save': 'Log+in',
    'atl_token': cookies['atl.xsrf.token']
}

response = r.post(
    url=url,
    headers=headers,
    cookies=cookies,
    data=form
)

# url = 'http://localhost:8085/plugins/servlet/applinks/auth/conf/oauth/outbound/apl/' + \
#       bitbucket_server + \
#       '?callback=' + \
#       bamboo_host + \
#       '/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
#       bamboo_server + \
#       '/INBOUND?oauth-incoming-enabled=true&uiposition=remote&hostUrl=http%3A%2F%2F10.0.2.15%3A8085&outgoing2LOEnabled=ENABLE_DISABLE_OUTGOING_TWO_LEGGED_OAUTH_PARAM&outgoing2LOiEnabled=ENABLE_DISABLE_OUTGOING_TWO_LEGGED_I_OAUTH_PARAM&enable-oauth=true'
#
# response = r.get(
#     url=url,
#     headers=headers,
#     cookies=cookies,
# )

url = 'http://localhost:8085/plugins/servlet/applinks/auth/conf/oauth/outbound/apl/' + \
      bitbucket_server + \
      '?callback=http://10.0.2.15:7990/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
      bamboo_server + \
      '/INBOUND?oauth-incoming-enabled=true&uiposition=remote&hostUrl=http%3A%2F%2Flocalhost%3A8085&outgoing2LOEnabled=ENABLE_DISABLE_OUTGOING_TWO_LEGGED_OAUTH_PARAM&outgoing2LOiEnabled=ENABLE_DISABLE_OUTGOING_TWO_LEGGED_I_OAUTH_PARAM&enable-oauth=true'


# url = 'http://localhost:8085/plugins/servlet/applinks/auth/conf/oauth/outbound/apl-2lo/' + \
#       bitbucket_server + \
#       '?callback=http://10.0.2.15:7990/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
#       bamboo_server + \
#       '/INBOUND?oauth-incoming-enabled=true&uiposition=remote&hostUrl=http%3A%2F%2F10.0.2.15%3A8085&outgoing2LOEnabled=true&outgoing2LOiEnabled=false&enable-outgoing-2lo=true&enable-outgoing-2loi=false'

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies
)

print response.status_code

url = 'http://10.0.2.15:7990/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
      bamboo_server + \
      '/INBOUND?oauth-incoming-enabled=true&uiposition=remote&hostUrl=http://localhost:8085&outgoing2LOEnabled=ENABLE_DISABLE_OUTGOING_TWO_LEGGED_OAUTH_PARAM&outgoing2LOiEnabled=ENABLE_DISABLE_OUTGOING_TWO_LEGGED_I_OAUTH_PARAM&success=true&message=Enabled+OAuth+authentication.'

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies
)


# print response.text
print response.status_code

time.sleep(2)

url = 'http://localhost:8085/plugins/servlet/applinks/auth/conf/oauth/outbound/apl-2lo/' + \
      bitbucket_server + \
      '?callback=http://10.0.2.15:7990/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
      bamboo_server + \
      '/INBOUND?oauth-incoming-enabled=true&uiposition=remote' \
      '&hostUrl=http%3A%2F%2Flocalhost%3A8085&' \
      '&outgoing2LOEnabled=true' \
      '&outgoing2LOiEnabled=false' \
      '&enable-outgoing-2lo=true' \
      '&enable-outgoing-2loi=false'

response = r.get(
    url=url,
    headers=headers,
    cookies=cookies
)

print response.status_code

modified_headers = headers

modified_headers['Host'] = '10.0.2.15:7990'

url = 'http://10.0.2.15:7990/plugins/servlet/applinks/auth/conf/oauth/add-consumer-by-url/' + \
      bamboo_server + \
      '/INBOUND?oauth-incoming-enabled=true' \
      '&uiposition=remote' \
      '&hostUrl=http://localhost:8085' \
      '&outgoing2LOEnabled=true' \
      '&outgoing2LOiEnabled=false' \
      '&outgoing_2lo_success=true' \
      '&message=Outgoing+2-Legged+OAuth+authentication+has+been+enabled.Outgoing+2-Legged+OAuth+authentication+with+Impersonation+has+been+disabled.'

response = r.get(
    url=url,
    headers=modified_headers,
    cookies=cookies
)

print response.status_code


