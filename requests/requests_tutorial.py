"""
https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
"""

import requests

# REQUEST HOOKS FOR EACH RESPONSE OBJECT
http = requests.Session()
assert_status_hook = lambda response, *arg, **kwargs: response.raise_for_status()
http.hooks['response'] = [assert_status_hook]
# raise exception 401 client error
http.get('https://api.github.com/user/repos?page=1')

# USE BASE URLS
from requests_toolbelt import sessions
http = sessions.BaseUrlSession(base_url='https://api.org')
print(http.get('/list').status_code)
print(http.get('/list/item').status_code)

# # SETTING DEFAULT TIMEOUTS
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5 

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
            del kwargs['timeout']
        super().__init__(*args,**kwargs)

        def send(self, request, **kwargs):
            timeout = kwargs.get('timeout')
            if timeout is None:
                kwargs['timeout'] = self.timeout
            return super().send(requests, **kwargs)

http = requests.Session()

# mount for both http/s usage
adapter = TimeoutHTTPAdapter(timeout=3)
http.mount('https://', adapter)
http.mount('http://', adapter)

# use default timeout
r = http.get("https://api.github.com/user/repos?page=1")
print(r.status_code)

# # overide timeout as needed
r = http.get('https://api.github.com/user/repos?page=1', timeout = 10)
print(r.status_code) 

# RETRY ON FAILURE
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(total=3, status_forcelist=[429,500,502,503,504], method_whitelist=['HEAD','GET','OPTIONS'])

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount('https://', adapter)
http.mount('http://', adapter)

r = http.get('https://en.wikipedia.org/w/api.php')
print(r.status_code)

# combine with timeout class
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))

# DEBUGGING HTTP REQUESTS
import http

# log http header
http.client.HTTPConnection.debuglevel = 1
requests.get('https://www.google.com/')

# log http request and response
from requests_toolbelt.utils import dump
def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))

http = requests.Session()
http.hooks['response'] = [logging_hook]

print(http.get('https://en.wikipedia.org/wiki/The_Lord_of_the_Rings'))

