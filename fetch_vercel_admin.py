import urllib.request
import sys

url = 'https://portfolio-ten-peach-17.vercel.app/admin/login/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        print('Status:', resp.status)
        # extract title if present
        start = html.find('<title>')
        end = html.find('</title>', start)
        if start != -1 and end != -1:
            title = html[start+7:end]
            print('Title:', title)
except Exception as e:
    print('Error:', e)
