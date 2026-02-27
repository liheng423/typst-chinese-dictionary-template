from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from sys import implementation
from typing import Dict, List, Tuple
from utils import is_cjk, load_rime_dict

import logging

logger = logging.getLogger(name=__name__)



class PinyinConverter(ABC):
    @abstractmethod
    def convert(
        self,
        text: str,
        style: str = "tone3",
        seg_sep: str = " ",
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def is_polyphonic(self, ch: str) -> bool:
        raise NotImplementedError
    





_vowel_tone_map = {
    "a": ["ā", "á", "ǎ", "à"],
    "e": ["ē", "é", "ě", "è"],
    "i": ["ī", "í", "ǐ", "ì"],
    "o": ["ō", "ó", "ǒ", "ò"],
    "u": ["ū", "ú", "ǔ", "ù"],
    "ü": ["ǖ", "ǘ", "ǚ", "ǜ"],
}


def _number_tone_to_diacritic(syl: str) -> str:
    m = re.match(r"^([a-züv]+)([1-5])?$", syl.lower())
    if not m:
        return syl
    base, t = m.group(1), m.group(2)
    base = base.replace("v", "ü")
    if not t or t == "5":
        return base
    tone = int(t)

    def mark(s: str, chars: str):
        for i, ch in enumerate(s):
            if ch in chars:
                return s[:i] + _vowel_tone_map[ch][tone - 1] + s[i + 1 :]
        return None

    for grp in ["a", "e", "o"]:
        r = mark(base, grp)
        if r:
            return r
    for pair in ["iu", "ui"]:
        k = base.find(pair)
        if k != -1:
            ch = pair[1]
            return base[: k + 1] + _vowel_tone_map[ch][tone - 1] + base[k + 2 :]
    for grp in ["i", "u", "ü"]:
        r = mark(base, grp)
        if r:
            return r
    return base


def _format_pinyin(piny: str, style: str) -> str:
    if style == "tone3": #tone is shown as number
        return piny
    if style == "normal": # no tone
        return re.sub(r"\d", "", piny)
    if style == "tone":
        return " ".join(_number_tone_to_diacritic(s) for s in piny.split())
    raise ValueError(f"Unknown style: {style}")


def _consume_braced_text(
    text: str,
    i: int,
    open_tag: str = "{",
    close_tag: str = "}",
) -> Tuple[str | None, int]:
    if i + 1 < len(text) and text[i + 1] == open_tag:
        pattern = r"^." + re.escape(open_tag) + r"([^" + re.escape(close_tag) + r"]*)" + re.escape(close_tag)
        m = re.match(pattern, text[i:])
        if not m:
            return None, i
        inner = m.group(1).strip()
        if len(inner) != 1:
            raise ValueError(f"Inline override must be exactly 1 char: '{inner}'")
        return inner, i + m.end()
    return None, i




@dataclass
class ShupinConverter(PinyinConverter):
    shupin_map: Dict[str, List[str]]
    max_word_len: int = 8

    def __post_init__(self):
        self._vocab = set(self.shupin_map.keys())
        if self._vocab:
            self.max_word_len = min(self.max_word_len, max(len(w) for w in self._vocab))

    def _longest_match(self, text: str, i: int) -> Tuple[str, int, bool]:
        end = min(len(text), i + self.max_word_len)
        for j in range(end, i, -1):
            seg = text[i:j]
            if seg in self._vocab:
                return seg, j, True
        return text[i : i + 1], i + 1, False

    def is_polyphonic(self, ch: str) -> bool:
        if ch == "?":
            return False
        readings = self.shupin_map.get(ch, [])
        return len(set(readings)) > 1
    
    def convert_char(
        self,
        ch: str,
        style: str,
        errors: list[tuple[int, str]],
        idx: int,
    ) -> str | None:
        if ch in self.shupin_map:
            readings = self.shupin_map[ch]
            chosen = "/".join(readings)
            if self.is_polyphonic(ch): logger.warning(f"The character {ch} is polyphonic, which requires manual proof. ")
            return _format_pinyin(chosen, style)
        if is_cjk(ch):
            errors.append((idx, ch))
            return None
        return ch

    def convert(
        self,
        text: str,
        style: str = "tone3",
        seg_sep: str = " ",
        escape_char: str = "?",
        embed_open: str = "{",
        embed_close: str = "}",
    ) -> str:
        out = []
        errors = []

        i = 0
        while i < len(text):
            inner, next_i = _consume_braced_text(text, i, open_tag=embed_open, close_tag=embed_close)
            if inner is not None:
                out.append(
                    self.convert(
                        inner,
                        style=style,
                        seg_sep=seg_sep,
                        escape_char=escape_char,
                        embed_open=embed_open,
                        embed_close=embed_close,
                    )
                )
                i = next_i
                continue

            ch = text[i]
            converted = self.convert_char(ch, style, errors, i)
            if converted is not None:
                out.append(converted)
            i += 1

        if errors:
            detail = "; ".join([f"pos {pos}: '{c}'" for pos, c in errors])
            raise ValueError(f"Characters not found in dict: {detail}")

        return seg_sep.join(s for s in out if s != "")


def build_shupin_converter(shupin_dict_path: str) -> ShupinConverter:
    return ShupinConverter(load_rime_dict(shupin_dict_path))
