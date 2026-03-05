import os
import rtoml
from pathlib import Path
from typing import Union, Iterable

from .pinyinconverter import build_shupin_converter
import logging
from .pinyinconverter import PinyinConverter
from ..utils import jian2fan_escape, read_csv_rows, write_csv_rows, load_config_fields
from .text_utils import process_outside_braces

LOG_NAME = "cvt_shupin"


class _DefaultRowFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "row"):
            record.row = "-"
        return True


def _init_logging(log_path: str = "logs/cvt_shupin.log", level: int = logging.INFO) -> None:
    logger_root = logging.getLogger(LOG_NAME)
    if logger_root.handlers:
        return
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.addFilter(_DefaultRowFilter())
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s row=%(row)s: %(message)s")
    )
    logger_root.setLevel(level)
    logger_root.addHandler(handler)


_init_logging()
logger = logging.getLogger(LOG_NAME)


def convert_csv_column(
    csv_path: Union[str, Path],
    src_col: str,
    dst_col: str,
    converter: PinyinConverter,
    style: str = "tone3",
    heteronym: bool = False,
    seg_sep: str = " ",
    out_path: Union[str, Path, None] = None,
    encoding: str = "utf-8",
    source_lang: str = "zh-cn",
    skip_chars: Iterable[str] = (),     # ← 新增：需要屏蔽的字符
    sep: str = ",",
    escape_path: Union[str, Path, None] = None,
    escape_section: str = "escape_map",
) -> list[dict[str, str]]:
    """
    读取 CSV，把 src_col 的汉字转换为拼音，结果写入 dst_col。
    - converter : 一个 ShupinConverter 对象
    - style     : 'tone3' | 'tone' | 'normal'
    - heteronym : 是否保留多音
    - seg_sep   : 字与字之间的分隔符
    - out_path  : 输出文件路径；如果 None 只返回 list
    - encoding  : 读写文件编码（默认 UTF-8)
    - skip_chars  : 一个可迭代对象，包含**需要跳过的单个字符**（如 ['※','〇']）
    """
    csv_path = Path(csv_path)
    rows, output_header = read_csv_rows(
        csv_path=str(csv_path),
        delimiter=sep,
        required_fields=[src_col],
        extra_columns=[dst_col],
        encoding=encoding,
    )


    skip_list = list(skip_chars)

    escape_map = {}
    if escape_path is not None:
        with open(escape_path, "r", encoding=encoding) as f:
            data = rtoml.load(f)
        escape_map = data.get(escape_section, {})
    escape_keys = sorted(escape_map.keys(), key=len, reverse=True)

    def _apply_escape_map(segment: str) -> str:
        if escape_keys:
            for key in escape_keys:
                segment = segment.replace(key, escape_map[key])
        return segment

    def _process_outside_braces(txt: str) -> str:
        if not txt:
            return ""

        def _convert_outside(segment: str) -> str:
            converted = []
            for ch in segment:
                converted.append(jian2fan_escape(ch, skip_list))
            return _apply_escape_map("".join(converted))

        return process_outside_braces(txt, _convert_outside)

    def _convert_text(txt):
        if txt is None:
            return ""
        txt = str(txt)

        return _process_outside_braces(txt)
    

    for row_idx, row in enumerate(rows, start=1):
        row[dst_col] = converter.convert(
            _convert_text(row.get(src_col, "")),
            log_ctx={"row": row_idx},
        )

    if out_path is not None:
        out_path = Path(out_path)
        write_csv_rows(
            csv_path=str(out_path),
            rows=rows,
            fieldnames=output_header,
            delimiter=sep,
            encoding=encoding,
        )

    return rows

if __name__ == "__main__":
    conv = build_shupin_converter("./assets/pinyin_schemes/shupin.dict.yaml")  
    
    # 假设 CSV 格式：
    # item,yixie,pinyin,label,class,def,ex,page
    # 四川話輸入法很有意思 事情,xxx,,...
    #
    rows_out = convert_csv_column(
        csv_path="./library/sichuanfangyan-test-2.csv",
        src_col="item",
        dst_col="pinyin",
        converter=conv,
        style="tone3",
        heteronym=False,
        out_path="./library/sichaunfangyan-test-2-sp.csv",
        source_lang="zh-cn",
        skip_chars=load_config_fields("./src/pinyin/configs.toml", section="skipchars", key="chars"),
        sep=load_config_fields("./src/pinyin/configs.toml", section="csv", key="delimiter")
    )
    print(rows_out[:5])

    
    
    
