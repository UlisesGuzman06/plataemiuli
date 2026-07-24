import requests, re

url = "https://plataemiuli.onrender.com/"
resp = requests.get(url)
print("Status Code:", resp.status_code)
if resp.status_code == 200:
    print("SUCCESS! Page title:", re.search(r'<title>(.*?)</title>', resp.text).group(1))
else:
    match_title = re.search(r'<title>(.*?)</title>', resp.text, re.DOTALL)
    if match_title:
        print("Title:", match_title.group(1).strip())
    pres = re.findall(r'<pre.*?>(.*?)</pre>', resp.text, re.DOTALL)
    for i, p in enumerate(pres[:3]):
        clean_p = p.replace('&quot;', '"').replace('&#x27;', "'").strip()
        print(f"Pre {i}:", clean_p[:200])
