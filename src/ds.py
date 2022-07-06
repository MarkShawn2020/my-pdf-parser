from typing import TypedDict, List

Point = List[float]


class RectWithTwoPoints(TypedDict):
    lt: Point
    rb: Point


class TextBox(RectWithTwoPoints):
    text: str
