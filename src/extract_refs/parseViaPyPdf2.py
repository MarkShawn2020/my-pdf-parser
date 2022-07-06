import json
import os
from typing import List, Iterator

import PyPDF2

from src.extract_refs.ds import CrossRefItem
from src.const import CONST_SAMPLE_FILE, DATA_PATH
from src.extract_refs.const import CONST_KEY_ANNOTS, CONST_KRY_URI, CONST_KEY_ANCHOR, CONST_KEY_RECT


def parseCrossrefWithUriOfPage(page) -> List[CrossRefItem]:
    uris: List[CrossRefItem] = []
    pageObject = page.getObject()
    if CONST_KEY_ANNOTS in pageObject.keys():
        ann = pageObject[CONST_KEY_ANNOTS]
        for a in ann:
            dictionaryObject = a.getObject()
            if CONST_KRY_URI in dictionaryObject[CONST_KEY_ANCHOR].keys():
                rect = list(map(float, dictionaryObject[CONST_KEY_RECT]))
                uri = dictionaryObject[CONST_KEY_ANCHOR][CONST_KRY_URI]
                uris.append({"url": uri, "lt": [rect[0], rect[3]], "rb": [rect[2], rect[1]]})
    return uris


def parseCrossrefWithUriFromFile(file, pageRanges: Iterator[int] = None) -> List[CrossRefItem]:
    PDFFile = open(file, 'rb')

    PDF = PyPDF2.PdfFileReader(PDFFile)
    pages = PDF.getNumPages()
    uris: List[CrossRefItem] = []

    # 参考：https://stackoverflow.com/a/56299671/9422455
    if not pageRanges:
        pageRanges = range(pages)
    for page in pageRanges:
        try:
            print("Current Page: {}".format(page))
            pageSliced = PDF.getPage(page)
            uris.extend(parseCrossrefWithUriOfPage(pageSliced))
        except IndexError:
            break
    return uris


if __name__ == '__main__':
    result = parseCrossrefWithUriFromFile(CONST_SAMPLE_FILE, range(20, 999))
    print(result)
    with open(os.path.join(DATA_PATH, "refs_crossref_uri.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
