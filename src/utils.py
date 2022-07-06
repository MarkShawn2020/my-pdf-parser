from src.ds import RectWithTwoPoints


def isRectIn(a: RectWithTwoPoints, b: RectWithTwoPoints, margin=2):
    """
    判断一个矩形是否在另一个矩形内
    :param a:
    :param b:
    :param margin:
    :return:
    """
    return \
        a["lt"][0] >= b["lt"][0] - margin and \
        a["lt"][1] <= b["lt"][1] + margin and \
        a["rb"][0] <= b["rb"][0] + margin and \
        a["rb"][1] >= b["rb"][1] - margin
