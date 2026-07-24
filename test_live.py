import requests, re

url = "https://plataemiuli.onrender.com/"
resp = requests.get(url)
text = resp.text

print("Status Code:", resp.status_code)
# find all occurrences of LINE 1 or SQL
for match in re.finditer(r'LINE 1:(.*?)\n', text):
    print("Match:", match.group(0))

# find code blocks in traceback
code_blocks = re.findall(r'<pre class="exception_value">(.*?)</pre>', text, re.DOTALL)
for cb in code_blocks:
    print("Exception Value Pre:", cb.strip())
