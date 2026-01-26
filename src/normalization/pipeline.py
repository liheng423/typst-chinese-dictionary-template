
import re
from pathlib import Path
from typing import Iterable, Iterator, Optional, Tuple

from studio import format_with_ai_studio
from regex import _compile_pattern, clean_page


CSV_HEADER = "item|yixie|pinyin|label|class|def|ex|page"


def _extract_rows(csv_text: str) -> list[str]:
    rows: list[str] = []
    for line in csv_text.splitlines():
        line = line.strip()
        if not line or line == CSV_HEADER:
            continue
        rows.append(line)
    return rows


def _row_item(row: str) -> str:
    if not row:
        return ""
    return row.split("|", 1)[0].strip()


def _previous_page_row(page: str, page_last_rows: dict[str, str]) -> str:
    if not page or not page.isdigit():
        return ""
    previous_page = str(int(page) - 1)
    return page_last_rows.get(previous_page, "")




def iter_matches(
    paths: Iterable[Path],
    pattern_key: str,
    encoding: str = "utf-8",
) -> Iterator[Tuple[Path, re.Match]]:
    pattern, flags = _compile_pattern(pattern_key)
    for path in paths:
        text = Path(path).read_text(encoding=encoding)
        for match in re.finditer(pattern, text, flags):
            yield Path(path), match


def run_pipeline(
    paths: Iterable[Path],
    pattern_key: str = "page",
    encoding: str = "utf-8",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    start_at: int = 0,
    existing_pages: Optional[set[str]] = None,
    page_last_rows: Optional[dict[str, str]] = None,
) -> Iterator[dict]:
    if start_at < 0:
        raise ValueError("start_at must be >= 0")
    page_set = existing_pages or set()
    page_rows = page_last_rows or {}
    for index, (path, match) in enumerate(iter_matches(paths, pattern_key, encoding=encoding)):
        if index < start_at:
            continue
        page = clean_page(match.group(1))
        previous_row = _previous_page_row(page, page_rows)
        previous_item = _row_item(previous_row)

        if page and page in page_set:
            yield {
                "index": index,
                "path": str(path),
                "page": page,
                "csv": "",
                "drop_previous": False,
                "skipped": True,
            }
            continue
        raw_text = match.group(2) 
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        if model:
            kwargs["model"] = model
        kwargs["page_number"] = page
        kwargs["last_word"] = previous_row
        csv_text = format_with_ai_studio(raw_text, **kwargs)
        rows = _extract_rows(csv_text)
        first_item = _row_item(rows[0]) if rows else ""
        drop_previous = bool(previous_item and first_item and previous_item == first_item)
        if rows:
            page_rows[page] = rows[-1]
        yield {
            "index": index,
            "path": str(path),
            "page": page,
            "csv": csv_text,
            "drop_previous": drop_previous,
            "skipped": False,
        }
