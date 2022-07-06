from src.extract_refs.ds import RefItem


def refs2md(hl: RefItem, index: int) -> str:
    """
    将结构化的超链接转成markdown
    :param hl:
    :param index:
    :return:
    """
    s = hl["text"]
    s = s[s.index(".") + 2:]
    for cref in hl["crefs"]:
        s = s.replace(cref["text"], f"{cref['text'][:-1]}:{cref['url']}]")
    return f"[^{index}]: {s}"