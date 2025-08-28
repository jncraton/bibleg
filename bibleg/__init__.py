import requests
import re

def get_text(ref, version="ESV"):
    res = requests.get(f"https://www.biblegateway.com/passage/?search={ref}&version={version}")

    assert res.status_code == 200

    html = res.content.decode()

    m = re.search(r'<div class="passage-text">(.*?)</div>', html, flags=re.I|re.DOTALL|re.M)

    assert m != None

    return m.group(0)