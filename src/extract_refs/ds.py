from typing import Optional, List

from src.ds import TextBox


class CrossRefItem(TextBox):
    url: str


class RefItem(TextBox):
    crefs: Optional[List[TextBox]]