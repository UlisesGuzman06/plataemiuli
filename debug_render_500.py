import requests, re

url = "https://plataemiuli.onrender.com/"
resp = requests.get(url)
text = resp.text

pres = re.findall(r'<pre.*?>(.*?)</pre>', text, re.DOTALL)
for i, p in enumerate(pres[:10]):
    clean_p = p.replace('&quot;', '"').replace('&#x27;', "'").strip()
    if clean_p and len(clean_p) < 300:
        print(f"Pre {i}: {clean_p}")
