import requests

def get_text(ref, version="ESV"):
    res = requests.get(f"https://www.biblegateway.com/passage/?search={ref}&version={version}")

    assert res.status_code == 200
    return res.text