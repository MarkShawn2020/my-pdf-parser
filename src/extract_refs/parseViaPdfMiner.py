import json
import os
import re
from typing import List, Iterator

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from src.extract_refs.ds import CrossRefItem, RefItem
from src.const import CONST_SAMPLE_FILE, DATA_PATH
from src.extract_refs.const import CONST_CROSS_REF, CONST_PUB_MED
from src.utils import isRectIn


def _parseBasicCrossrefFromPage(page) -> List[CrossRefItem]:
    """
    将char_margin调到精确的0.5左右，可以获得 [CrossRef] 之类较好的单词分割效果
    :param page:
    :return:
    """
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(char_margin=0.5, boxes_flow=None, line_margin=0)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    interpreter.process_page(page)

    items: List[CrossRefItem] = []

    for box in device.get_result():  # type: LTTextBox
        if isinstance(box, LTTextBox):
            text = box.get_text().strip(" \n")
            # print(f"'{text}'")
            if CONST_CROSS_REF in text or CONST_PUB_MED in text:
                items.append({"text": text, "lt": [box.x0, box.y1], "rb": [box.x1, box.y0], "url": ''})

    return items


def _parseBasicRefsFromPage(page: PDFPage) -> List[RefItem]:
    """
    将char_margin调大，可以获得完整的一整行句子
    :param page:
    :return:
    """
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(char_margin=200, boxes_flow=None, line_margin=0)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    interpreter.process_page(page)
    interpreter.process_page(page)

    items: List[RefItem] = []

    for box in device.get_result():  # type: LTTextBox
        if isinstance(box, LTTextBox):
            text = box.get_text().strip(" \n")
            x0 = box.x0
            if x0 < 40:
                # if "2. Jinyu" in text:
                #     # (35.716, 352.6904752, 559.2780949504001, 361.6568752)
                #     print()
                items.append({"text": text, "lt": [box.x0, box.y1], "rb": [box.x1, box.y0], "crefs": []})
            else:
                # (57.232, 341.1834752, 406.74735039999996, 350.3381696)
                items[-1]["text"] += text
                items[-1]["rb"][1] = box.y0

    items = [i for i in items if re.match(r"\d+\.", i["text"])]
    return items


def parseRefWithCrossrefFromPage(page) -> List[RefItem]:
    """
    这个函数本身是没有问题的，如果一个crossref在本页被检测到，它就一定会被解析到ref内
    但问题在于，连页问题将导致下一页开头的第一句话无法解析，因此必要时还得基于file级别连解
    :param page:
    :return:
    """
    refs: List[RefItem] = _parseBasicRefsFromPage(page)
    crefs: List[CrossRefItem] = _parseBasicCrossrefFromPage(page)
    j = 0
    for ref in refs:
        if CONST_CROSS_REF in ref["text"]:
            # print("detecting " + CONST_CROSS_REF)
            cRef = crefs[j]
            assert isRectIn(cRef, ref, margin=0)
            ref["crefs"].append(cRef)
            j += 1

        if CONST_PUB_MED in ref["text"]:
            # print("detecting " + CONST_PUB_MED)
            cRef = crefs[j]
            assert isRectIn(cRef, ref, margin=0)
            ref["crefs"].append(cRef)
            j += 1

    assert j == len(crefs), {"j": j, "len(cross_refs)": len(crefs)}

    return refs


def parseRefsWithCrossrefFromFile(file: str, pageRanges: Iterator = None) -> List[RefItem]:
    fp = open(file, 'rb')

    pages = list(PDFPage.get_pages(fp))
    if not pageRanges:
        _pageRanges = range(len(pages))
    else:
        _pageRanges = []
        for i in pageRanges:
            if 0 <= i and i < len(pages):
                _pageRanges.append(i)

    refs: List[RefItem] = []
    for page_i in _pageRanges:
        refs.extend(parseRefWithCrossrefFromPage(pages[page_i]))
    return refs


if __name__ == '__main__':
    result = parseRefsWithCrossrefFromFile(CONST_SAMPLE_FILE, range(20, 999))
    print(result)
    with open(os.path.join(DATA_PATH, "refs_crossref_base.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
