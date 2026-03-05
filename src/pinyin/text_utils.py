from typing import Callable


def process_outside_braces(
    text: str,
    on_outside: Callable[[str], str],
    on_inside: Callable[[str], str] | None = None,
    open_brace: str = "{",
    close_brace: str = "}",
) -> str:
    if not text:
        return ""

    if on_inside is None:
        def temp_on_inside(segment: str) -> str:
            return segment
        on_inside = temp_on_inside

    out: list[str] = []
    outside_buf: list[str] = []
    depth = 0

    def flush_outside() -> None:
        if not outside_buf:
            return
        segment = on_outside("".join(outside_buf))
        out.append(segment)
        outside_buf.clear()

    for ch in text:
        if ch == open_brace:
            if depth == 0:
                flush_outside()
            depth += 1
            out.append(ch)
            continue
        if ch == close_brace:
            if depth > 0:
                depth -= 1
            out.append(ch)
            continue
        if depth == 0:
            outside_buf.append(ch)
        else:
            out.append(on_inside(ch))

    flush_outside()
    return "".join(out)
