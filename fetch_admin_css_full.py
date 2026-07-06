import urllib.request, re, sys

BASE = 'https://portfolio-ten-peach-17.vercel.app'
url = BASE + '/admin/login/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        print('Page status:', resp.status)
        css_links = re.findall(r'href=["\']([^\"\']+\.css)["\']', html)
        print('Found CSS links:', len(css_links))
        for link in css_links[:5]:
            full_url = link if link.startswith('http') else BASE + link
            try:
                cr = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(cr) as css_resp:
                    print('Fetched', full_url, 'status', css_resp.status)
            except Exception as e:
                print('Error fetching', full_url, e)
except Exception as e:
    print('Error loading page:', e)
