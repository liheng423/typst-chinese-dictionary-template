import sys
from pathlib import Path
from typing import Iterable

import config
import pipeline


def _collect_paths(inputs: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            paths.extend(sorted(p for p in path.rglob("*") if p.is_file()))
        else:
            paths.append(path)
    return paths


def _read_last_index(path: str) -> int | None:
    try:
        text = Path(path).read_text(encoding=config.ENCODING).strip()
    except FileNotFoundError:
        return None
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _write_last_index(path: str, index: int) -> None:
    Path(path).write_text(str(index), encoding=config.ENCODING)


def _remove_last_csv_row(path: str) -> None:
    try:
        lines = Path(path).read_text(encoding=config.ENCODING).splitlines()
    except FileNotFoundError:
        return
    for index in range(len(lines) - 1, -1, -1):
        line = lines[index].strip()
        if not line or line == pipeline.CSV_HEADER:
            continue
        del lines[index]
        break
    Path(path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding=config.ENCODING)


def _remove_row(path: str, row: str) -> bool:
    if not row:
        return False
    try:
        lines = Path(path).read_text(encoding=config.ENCODING).splitlines()
    except FileNotFoundError:
        return False
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].strip() == row:
            del lines[index]
            Path(path).write_text(
                "\n".join(lines) + ("\n" if lines else ""),
                encoding=config.ENCODING,
            )
            return True
    return False


def _read_page_last_rows(path: str) -> dict[str, str]:
    try:
        lines = Path(path).read_text(encoding=config.ENCODING).splitlines()
    except FileNotFoundError:
        return {}
    page_rows: dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line or line == pipeline.CSV_HEADER:
            continue
        parts = line.rsplit("|", 1)
        if len(parts) != 2:
            continue
        page = parts[1].strip()
        if page:
            page_rows[page] = line
    return page_rows


def main() -> int:
    paths = _collect_paths(config.INPUT_PATHS)
    if not paths:
        print("No input files found.", file=sys.stderr)
        return 2

    start_at = config.START_AT
    page_last_rows = _read_page_last_rows(config.OUTPUT_PATH)
    existing_pages = set(page_last_rows.keys())
    if config.RESUME_FROM_LOG:
        last_index = _read_last_index(config.LOG_PATH)
        if last_index is not None and last_index > start_at:
            start_at = last_index

    for item in pipeline.run_pipeline(
        paths,
        pattern_key=config.PATTERN_KEY,
        encoding=config.ENCODING,
        api_key=config.API_KEY,
        model=config.DEFAULT_MODEL,
        start_at=start_at,
        existing_pages=existing_pages,
        page_last_rows=page_last_rows,
    ):
        if config.LOG_EVERY > 0 and item["index"] % config.LOG_EVERY == 0:
            print(
                f"[{item['index']}] page={item['page']} path={item['path']}",
                file=sys.stderr,
            )
        if item.get("skipped"):
            print(
                f"[{item['index']}] page={item['page']} exists, skipping",
                file=sys.stderr,
            )
            _write_last_index(config.LOG_PATH, item["index"])
            continue
        if item.get("drop_previous"):
            _remove_row(config.OUTPUT_PATH, page_last_rows.get(str(int(item["page"]) - 1), ""))
        with open(config.OUTPUT_PATH, "a", encoding=config.ENCODING) as output_handle:
            output_handle.write(item["csv"].rstrip() + "\n")
        _write_last_index(config.LOG_PATH, item["index"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
