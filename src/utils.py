
import csv
import re
import rtoml
from typing import Any, Callable, Dict, List, Tuple
from zhconv import convert
# ============ REGEX ===============


RE_CJK = re.compile(r"[\u3400-\u9FFF\uF900-\uFAFF]")
RE_IS_HANZI = r'^[\u4e00-\u9fff]'

is_hanzi: Callable[[str], bool] = lambda s: bool(re.match(re.compile(RE_IS_HANZI), s))
is_cjk: Callable[[str], bool] = lambda s: bool(re.match(RE_CJK, s))


# ============ CSV ====================


def load_config_fields(
    config_path: str,
    section: str,
    key: str = "fields",
    default: list[str] | None = None,
) -> Any:
    if default is None:
        default = []
    with open(config_path, "r", encoding="utf-8") as f:
        data = rtoml.load(f)
    return data.get(section, {}).get(key, default)


def load_config_section(config_path: str, section: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        data = rtoml.load(f)
    return data.get(section, {})


def safe_list_get(
    values: list[str | None],
    index: int,
    default: str = "none",
) -> str:
    if index < 0:
        return default
    if index >= len(values):
        return default
    value = values[index]
    return value if value is not None else default


def read_csv_rows(
    csv_path: str,
    delimiter: str,
    required_fields: list[str] | None = None,
    extra_columns: list[str] | None = None,
    encoding: str = "utf-8",
) -> tuple[list[dict[str, str]], list[str]]:
    if required_fields is None:
        required_fields = []
    if extra_columns is None:
        extra_columns = []
    with open(csv_path, "r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        header = list(reader.fieldnames or [])
        missing = [col for col in required_fields if col not in header]
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")
        output_header = header + [col for col in extra_columns if col not in header]
        rows = list(reader)
    return rows, output_header


def write_csv_rows(
    csv_path: str,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    delimiter: str,
    encoding: str = "utf-8",
) -> None:
    with open(csv_path, "w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)

    
    print(f"[INFO] Wrote CSV with pinyin column: {csv_path}")
# ========== LOAD RIME =======================




def load_rime_dict(path: str) -> Dict[str, List[str]]:
    """
    Parse RIME .dict.yaml into {word: [pinyin1, pinyin2, ...]}.
    """
    entries: Dict[str, List[str]] = {}
    in_table = False
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not in_table:
                if line == "...":
                    in_table = True
                continue
            if not line or line.startswith("#"):
                continue
            cols = re.split(r"\s+", line)
            if len(cols) < 2:
                continue
            word = cols[0]
            piny = " ".join(cols[1].split()).lower()
            if "◎" in piny:
                piny = piny.split("◎", 1)[0].strip()
            entries.setdefault(word, [])
            if piny not in entries[word]:
                entries[word].append(piny)
    if not entries:
        raise ValueError("Empty dict: no entries parsed from shupin.dict.yaml")
    return entries



# ================ fan jian converter ====================

def jian2fan(ch: str) -> str:
    
    return convert(ch, "zh-tw")

def jian2fan_escape(ch: str, escape_list: List[str]) -> str:

    if ch in escape_list:
        return ch
    return jian2fan(ch)
