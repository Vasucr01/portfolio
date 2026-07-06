import urllib.request, re, sys

url = 'https://portfolio-ten-peach-17.vercel.app/admin/login/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        print('Status:', resp.status)
        # extract all href links ending with .css
        css_links = re.findall(r'href=["\']([^\"\']+\.css)["\']', html)
        print('CSS links found:', len(css_links))
        for link in css_links[:5]:
            print(' -', link)
            # fetch each css
            css_req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(css_req) as css_resp:
                    print('   CSS status:', css_resp.status)
            except Exception as e:
                print('   CSS fetch error:', e)
except Exception as e:
    print('Error fetching page:', e)
