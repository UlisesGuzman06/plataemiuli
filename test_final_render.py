import requests, re

url = "https://plataemiuli.onrender.com/"
resp = requests.get(url)
print("Status Code:", resp.status_code)
if resp.status_code == 200:
    print("SUCCESS! Page title:", re.search(r'<title>(.*?)</title>', resp.text).group(1))
else:
    match_val = re.search(r'<th>Exception Value:</th>\s*<td><pre>(.*?)</pre>', resp.text, re.DOTALL)
    if match_val:
        print("Exception Value:", match_val.group(1).strip())
    else:
        pres = re.findall(r'<pre.*?>(.*?)</pre>', resp.text, re.DOTALL)
        for i, p in enumerate(pres[:3]):
            clean_p = p.replace('&quot;', '"').replace('&#x27;', "'").strip()
            print(f"Pre {i}:", clean_p[:200])
