import requests
import re

def get_text(ref, version="ESV"):
    res = requests.get(f"https://www.biblegateway.com/passage/?search={ref}&version={version}")

    assert res.status_code == 200

    html = res.content.decode()

    m = re.search(r'<div class="passage-text">(.*?)<div class="passage-scroller', html, flags=re.I|re.DOTALL|re.M)

    assert m != None

    passage_html = m.group(1)
    passage_html = re.sub(r'<div class="footnotes.*', "", passage_html, flags=re.I|re.DOTALL|re.M)
    passage_html = re.sub(r'<div class="passage-other-trans.*', "", passage_html, flags=re.I|re.DOTALL|re.M)
    passage_html = re.sub(r'<div class="crossrefs.*', "", passage_html, flags=re.I|re.DOTALL|re.M)
    passage_html = re.sub(r'<a class="full-chap-link.*', "", passage_html, flags=re.I|re.DOTALL|re.M)

    passage_html = re.sub(r'(<h\d>).*?</h\d>', "", passage_html)
    passage_html = re.sub(r'(</p>)', "\1\n\n", passage_html)
    passage_html = re.sub(r'<br.*?>', "\n\n", passage_html)
    passage_html = re.sub(r'&nbsp;', " ", passage_html)

    # Remove crossrefs, verse numbers, and chapter numbers
    passage_html = re.sub(r'<sup.*?</sup>', "", passage_html)
    passage_html = re.sub(r'<span class="chapternum">.*?</span>', "", passage_html)

    # Remove HTML tags and convert to plain text
    passage_text = re.sub(r"<.*?>", "", passage_html)

    # Remove leading whitespace
    passage_text = re.sub(r'\n[ \t]+', '\n', passage_text)

    # Remove trailing whitespace
    passage_text = re.sub(r'[ \t]+\n', '\n', passage_text)

    return passage_text.strip()