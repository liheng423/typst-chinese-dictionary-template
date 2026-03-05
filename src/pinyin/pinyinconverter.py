from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from sys import implementation
from typing import Dict, List, Tuple, Mapping, Any
from ..utils import is_cjk, load_rime_dict, jian2fan

import logging

logger = logging.getLogger(name="cvt_shupin")



class PinyinConverter(ABC):
    @abstractmethod
    def convert(
        self,
        text: str,
        style: str = "tone3",
        seg_sep: str = " ",
        log_ctx: Mapping[str, Any] | None = None,
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


def _consume_braced_content(
    text: str,
    i: int,
    open_tag: str = "{",
    close_tag: str = "}",
) -> Tuple[str | None, int]:
    if i >= len(text) or text[i] != open_tag:
        return None, i
    end = text.find(close_tag, i + 1)
    if end == -1:
        raise ValueError(f"Unclosed brace at pos {i}")
    inner = text[i + 1 : end]
    return inner, end + 1


def _consume_quoted_text(text: str, i: int, quote: str = '"') -> Tuple[str | None, int]:
    if i >= len(text) or text[i] != quote:
        return None, i
    end = text.find(quote, i + 1)
    if end == -1:
        raise ValueError(f"Unclosed quote at pos {i}")
    inner = text[i + 1 : end]
    return inner, end + 1




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
        log: logging.LoggerAdapter,
    ) -> str | None:
        """Convert a single character to pinyin (or pass through).

        Args:
            ch (str): Single character to convert.
            style (str): Pinyin style to format with.
            errors (list[tuple[int, str]]): Collects (index, char) for CJK chars without a mapping.
            idx (int): Absolute character index for error reporting.
            log (logging.LoggerAdapter): Logger adapter for warnings.

        Returns:
            str | None: Converted text for this character, None if missing mapping.
        """
        if ch in self.shupin_map:
            readings = self.shupin_map[ch]
            chosen = "/".join(readings)
            if self.is_polyphonic(ch):
                log.warning(
                    "pos %s: The character %s is polyphonic, which requires manual proof.",
                    idx,
                    ch,
                )
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
        log_ctx: Mapping[str, Any] | None = None,
    ) -> str:
        log = logging.LoggerAdapter(logger, dict(log_ctx or {}))
        def _warn_polyphonic(seg: str, idx: int) -> None:
            readings = self.shupin_map.get(seg, [])
            if len(set(readings)) > 1:
                log.warning(
                    "pos %s: The word %s is polyphonic, which requires manual proof.",
                    idx,
                    seg,
                )

        def _convert_segment_with_words(
            segment: str,
            base_idx: int,
            use_jian2fan: bool,
        ) -> list[str]:
            out_seg: list[str] = []
            if use_jian2fan:
                norm = "".join(jian2fan(ch) if is_cjk(ch) else ch for ch in segment)
            else:
                norm = segment

            i = 0
            while i < len(segment):
                seg, next_i, matched = self._longest_match(norm, i)
                if matched and len(seg) > 1:
                    readings = self.shupin_map[seg]
                    chosen = "/".join(readings)
                    _warn_polyphonic(seg, base_idx + i)
                    out_seg.append(_format_pinyin(chosen, style))
                    i = next_i
                    continue

                ch_norm = norm[i]
                converted = self.convert_char(ch_norm, style, errors, base_idx + i, log=log)
                if converted is not None:
                    out_seg.append(converted)
                i += 1
            return out_seg

        def _convert_with_quotes(inner: str, base_idx: int) -> list[str]:
            out_inner: list[str] = []
            j = 0
            while j < len(inner):
                quoted, next_j = _consume_quoted_text(inner, j, quote='"')
                if quoted is not None:
                    out_inner.append(quoted)
                    j = next_j
                    continue
                next_quote = inner.find('"', j)
                if next_quote == -1:
                    out_inner.extend(_convert_segment_with_words(inner[j:], base_idx + j, True))
                    break
                if next_quote > j:
                    out_inner.extend(
                        _convert_segment_with_words(inner[j:next_quote], base_idx + j, True)
                    )
                j = next_quote
            return out_inner

        out = []
        errors = []

        def _convert_plain_segment(segment: str, base_idx: int) -> None:
            for offset, ch in enumerate(segment):
                abs_idx = base_idx + offset
                if ch == "(":
                    close_paren = text.find(")", abs_idx + 1)
                    if (
                        close_paren != -1
                        and close_paren + 1 < len(text)
                        and text[close_paren + 1] == embed_open
                    ):
                        end = text.find(embed_close, close_paren + 2)
                        if end == -1:
                            raise ValueError(f"Unclosed brace at pos {close_paren + 1}")
                if abs_idx + 1 < len(text) and text[abs_idx + 1] == embed_open:
                    end = text.find(embed_close, abs_idx + 2)
                    if end == -1:
                        raise ValueError(f"Unclosed brace at pos {abs_idx + 1}")
                if ch == '"':
                    raise ValueError(f'Quoted text is only allowed inside braces: pos {abs_idx}')
                out.extend(_convert_segment_with_words(segment[offset:], abs_idx, False))
                return

        # Inline override:
        # 1) (AA){BB} -> output BB (convert BB), skip AA entirely
        # 2) X{BB} -> output BB (convert BB), ignore X
        pattern = re.compile(
            rf"\([^)]*\){re.escape(embed_open)}[^{re.escape(embed_close)}]*{re.escape(embed_close)}"
            rf"|[\s\S]{re.escape(embed_open)}[^{re.escape(embed_close)}]*{re.escape(embed_close)}"
        )

        pos = 0
        for m in pattern.finditer(text):
            if m.start() > pos:
                _convert_plain_segment(text[pos:m.start()], pos)

            if text[m.start()] == "(":
                brace_idx = text.find(embed_open, m.start(), m.end())
            else:
                brace_idx = m.start() + 1

            inner, next_i = _consume_braced_content(
                text, brace_idx, open_tag=embed_open, close_tag=embed_close
            )
            if inner is not None:
                out.extend(_convert_with_quotes(inner, brace_idx))
                pos = next_i
                continue

            pos = m.end()

        if pos < len(text):
            _convert_plain_segment(text[pos:], pos)

        if errors:
            detail = "; ".join([f"pos {pos}: '{c}'" for pos, c in errors])
            row_info = ""
            if log_ctx and "row" in log_ctx:
                row_info = f" row {log_ctx['row']}:"
            raise ValueError(f"Characters not found in dict:{row_info} {detail}")

        return seg_sep.join(s for s in out if s != "")


def build_shupin_converter(shupin_dict_path: str) -> ShupinConverter:
    return ShupinConverter(load_rime_dict(shupin_dict_path))
