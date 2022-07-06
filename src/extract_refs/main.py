import json
import os

from src.const import DATA_PATH
from src.extract_refs.ds import CrossRefItem, RefItem
from src.utils import isRectIn
from src.extract_refs.utils import refs2md

if __name__ == '__main__':

    # 1. integrate refs with crossrefs
    with open(os.path.join(DATA_PATH, "refs_crossref_base.json"), "r") as f:
        refs = json.load(f)

    with open(os.path.join(DATA_PATH, "refs_crossref_uri.json"), "r") as f:
        crefs = json.load(f)

    j = 0
    for ref in refs:  # type: RefItem
        # print(ref["text"])
        for cref1 in ref["crefs"]:  # type: CrossRefItem
            while True:
                cref2 = crefs[j]  # type:
                j += 1
                if isRectIn(cref2, cref1):
                    cref1["url"] = cref2["url"]
                    break

    with open(os.path.join(DATA_PATH, "refs.json"), "w") as f:
        json.dump(refs, f, ensure_ascii=False, indent=2)

    # 2. refs to markdown
    with open(os.path.join(DATA_PATH, "refs.json"), "r") as f1:
        with open(os.path.join(DATA_PATH, "refs.md"), "w") as f2:
            s = "\n\n".join(refs2md(hl, index + 1) for index, hl in enumerate(json.load(f1)))
            f2.write(s)
