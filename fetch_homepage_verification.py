import urllib.request, re, sys

BASE_URL = 'https://vasuchauhan.me/'  # custom domain, should point to Vercel
req = urllib.request.Request(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        # look for the verification meta tag
        m = re.search(r'<meta\s+name=["\']google-site-verification["\']\s+content=["\'][^"\']+["\']\s*/?>', html, re.I)
        if m:
            print('Verification tag found:', m.group(0))
        else:
            print('Verification tag NOT found')
        # optional: dump a snippet
        print('--- snippet start ---')
        print(html[:500])
        print('--- snippet end ---')
except Exception as e:
    print('Error fetching page:', e)
