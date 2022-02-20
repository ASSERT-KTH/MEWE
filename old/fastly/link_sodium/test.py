
import requests
session = requests.Session()
url='https://totally-devoted-krill.edgecompute.app'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Cache-Control': 'private, max-age=0, no-cache',
    'Connection': 'keep-alive',
    'Host': 'totally-devoted-krill.edgecompute.app',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br'
}

r = []
import sys
for i in range(100000):
    sys.stdout.write(f"\r{i}/100000")
    response = session.get(url, headers=headers)
    t = response.headers['xtime']
    t = int(t)
    r.append(t)

import json

open("time4binbase64.json", "w").write(json.dumps(r))
'''
	'''