import urllib.request
import re

req = urllib.request.Request('http://127.0.0.1:8000/admin/login/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req)
    print('Status:', res.status)
except Exception as e:
    html = e.read().decode('utf-8')
    title_match = re.search(r'<title>(.*?)</title>', html)
    if title_match:
        print('Title:', title_match.group(1))
    
    val_match = re.search(r'<div class="exception_value">([^<]+)</div>', html)
    if val_match:
        print('Exception:', val_match.group(1))
    else:
        print("Couldn't find exception div")
