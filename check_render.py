import requests, re

url = "https://plataemiuli.onrender.com/"
try:
    resp = requests.get(url)
    print("Status Code:", resp.status_code)
    if resp.status_code != 200:
        match_val = re.search(r'<th>Exception Value:</th>\s*<td><pre>(.*?)</pre>', resp.text, re.DOTALL)
        if match_val:
            print("Exception Value:", match_val.group(1).strip())
        else:
            pres = re.findall(r'<pre.*?>(.*?)</pre>', resp.text, re.DOTALL)
            for i, p in enumerate(pres[:3]):
                print(f"Pre {i}:", p.strip()[:200])
    else:
        print("SUCCESS! Page title:", re.search(r'<title>(.*?)</title>', resp.text).group(1))
except Exception as e:
    print("Request failed:", e)
