import requests
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('user', 'pass')

print(requests.get('https://httpbin.org/basic-auth/user/pass', auth=auth))
