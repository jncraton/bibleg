from urllib.request import urlopen
from urllib.parse import urlencode
import re

BOOKS = [
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
]


def get_text(ref, version="ESV"):
    """
    >>> get_text("John 11:35")
    'Jesus wept.'

    >>> get_text("Gen 1:1")
    'In the beginning, God created the heavens and the earth.'
    """

    params = {"search": ref, "version": version}
    query = urlencode(params, doseq=True, safe="")
    url = f"https://www.biblegateway.com/passage/?{query}"

    with urlopen(url) as resp:
        html = resp.read().decode()
        assert resp.status == 200

    m = re.search(
        r'<div class="passage-text">(.*?)<div class="passage-scroller',
        html,
        flags=re.I | re.DOTALL | re.M,
    )

    assert m is not None

    passage_html = m.group(1)

    # Trim trailing UI elements
    passage_html = re.sub(
        r'<div class="footnotes.*', "", passage_html, flags=re.I | re.DOTALL | re.M
    )
    passage_html = re.sub(
        r'<div class="passage-other-trans.*',
        "",
        passage_html,
        flags=re.I | re.DOTALL | re.M,
    )
    passage_html = re.sub(
        r'<div class="crossrefs.*', "", passage_html, flags=re.I | re.DOTALL | re.M
    )
    passage_html = re.sub(
        r'<a class="full-chap-link.*', "", passage_html, flags=re.I | re.DOTALL | re.M
    )

    # Remove headings
    passage_html = re.sub(r"(<h\d>).*?</h\d>", "", passage_html)

    # Add appropriate plaintext whitespace
    passage_html = re.sub(r"(</p>)", "\1\n\n", passage_html)
    passage_html = re.sub(r"<br.*?>", "\n\n", passage_html)
    passage_html = re.sub(r"&nbsp;", " ", passage_html)
    passage_html = re.sub(r"\x01", "", passage_html)

    # Remove crossrefs, verse numbers, and chapter numbers
    passage_html = re.sub(r"<sup.*?</sup>", "", passage_html)
    passage_html = re.sub(r'<span class="chapternum">.*?</span>', "", passage_html)

    # Remove HTML tags and convert to plain text
    passage_text = re.sub(r"<.*?>", "", passage_html)

    # Remove leading whitespace
    passage_text = re.sub(r"\n[ \t]+", "\n", passage_text)

    # Remove trailing whitespace
    passage_text = re.sub(r"[ \t]+\n", "\n", passage_text)

    return passage_text.strip()


def normalize_verse_ref(ref):
    """
    >>> normalize_verse_ref("Gen 1:1")
    (1, 1, 1)

    >>> normalize_verse_ref("Gen. 1:1")
    (1, 1, 1)

    >>> normalize_verse_ref("Ge 2:3")
    (1, 2, 3)

    >>> normalize_verse_ref("genesis 4:5")
    (1, 4, 5)

    >>> normalize_verse_ref("1 cor 12:3")
    (46, 12, 3)

    >>> normalize_verse_ref("2 cor 01:02")
    (47, 1, 2)

    >>> normalize_verse_ref("jas 3:2")
    (59, 3, 2)
    """

    book_codes = {
        "Jas": "James",
    }

    book_chapter_verse = re.match(r"(.*?)[\t \.]*(\d+):(\d+)$", ref.strip().title())

    if book_chapter_verse:
        book_idx = None
        book_needle = book_chapter_verse[1]

        if book_needle in book_codes:
            book_needle = book_codes[book_needle]

        for i, book in enumerate(BOOKS):
            if book.startswith(book_needle):
                book_idx = i + 1
                break
        else:
            raise IndexError(f"Book not found: {book_chapter_verse[1]}")

        chapter = int(book_chapter_verse[2])
        verse = int(book_chapter_verse[3])

        return book_idx, chapter, verse
    else:
        raise ValueError(f"Incorrect reference format: {ref}")


def get_verse_list(ref):
    """Return list of verses from a larger reference

    Only explicit spans are currently supported (e.g. Gen 1:2-3)

    Reference may not span chapters.

    Whole chapters are not currently supported.

    >>> get_verse_list("Gen 1:1")
    [(1, 1, 1)]

    >>> get_verse_list("Ex 2:3-5")
    [(2, 2, 3), (2, 2, 4), (2, 2, 5)]

    >>> get_verse_list("Gen. 3:6-8")
    [(1, 3, 6), (1, 3, 7), (1, 3, 8)]

    >>> get_verse_list("Lev 5:3,10")
    [(3, 5, 3), (3, 5, 10)]

    >>> get_verse_list("Gen 1")
    Traceback (most recent call last):
    ...
    IndexError: Whole chapters not supported: Gen 1

    >>> get_verse_list("Gen 1:1-2:1")
    Traceback (most recent call last):
    ...
    IndexError: Multi-chapter spans not supported: Gen 1:1-2:1
    """

    if ref.count(":") == 0:
        raise IndexError(f"Whole chapters not supported: {ref}")

    if ref.count(":") > 1:
        raise IndexError(f"Multi-chapter spans not supported: {ref}")

    ref = ref.strip()

    m_range = re.match(r"(.*?)(\d+)\-(\d+)$", ref)
    m_list = re.match(r"(.*?)([\d, ]+)$", ref)

    if m_range:
        root = m_range[1]
        v_start = int(m_range[2])
        v_end = int(m_range[3])

        return [normalize_verse_ref(f"{root}{v}") for v in range(v_start, v_end + 1)]
    elif m_list:
        root = m_list[1]
        verses = [v.strip() for v in m_list[2].split(",")]

        return [normalize_verse_ref(f"{root}{v}") for v in verses]
    else:
        return [normalize_verse_ref(ref)]
