
from typing import TypedDict


class GlossaryEntry(TypedDict):
    item: str
    pinyin: str
    benzi: str
    mean: list[list[str]]
    category: str
    pos: str
    definition: str
    examples: list[str]