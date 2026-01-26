import os
import json
import argparse
from collections import defaultdict
from typing import Dict
from pinyin.typedef import GlossaryEntry
from utils import safe_list_get
from utils import load_config_section, is_hanzi, read_csv_rows
import logging


logger = logging.getLogger(name=__name__)


def _norm_text(value) -> None | str:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def is_valid_entry(item: str, pinyin: str) -> bool:

    # 跳过空行或无拼音 
    if not item or not pinyin:
        logger.warning("missing pinyin row %s", is_valid_entry.__name__)
        return False

    # 跳过非汉字开头的词条
    if not is_hanzi(item):
        logger.warning("missing hanzi row %s", is_valid_entry.__name__)
        return False
    return True

def csv_to_glossary_json(
    csv_path: str,
    output_path: str,
    config_path: str,
    encoding: str = "utf-8",
) -> None:
    """
    将 item,yixie,pinyin,label,class,def,ex,page 格式的 CSV
    转换为 glossary.json 格式。
    自动跳过非汉字开头的 item。
    """

    grouped: Dict[str, GlossaryEntry] = dict()

        

    csv_config = load_config_section(config_path=config_path, section="csv")
    output_config = load_config_section(config_path=config_path, section="output")
    mean_config = output_config.get("mean", {})

    fields = csv_config.get("fields", [])
    delimiter = csv_config.get("delimiter", "|")
    examples_sep = mean_config.get("example_sep", ";") 
    example_columns = mean_config.get("example_columns", [])
    example_column = example_columns[0] if example_columns else None
    

    rows, header = read_csv_rows(
        csv_path=str(csv_path),
        delimiter=delimiter,
        required_fields=fields,
        encoding=encoding,
    )
    example_col = example_column if example_column in header else None
    for row in rows:
        values = [_norm_text(row.get(col, "")) for col in fields]
        item = safe_list_get(values, 0)
        pinyin = safe_list_get(values, 1)
        benzi = safe_list_get(values, 2, "") or ""
        label = safe_list_get(values, 3)
        pos = safe_list_get(values, 4)
        definition = safe_list_get(values, 5)


        if not is_valid_entry(item, pinyin):
            continue
        
        # preocess example texts
        examples = []
        if example_col:
            example_value = _norm_text(row.get(example_col, ""))
            if example_value:
                for e in example_value.split(examples_sep):
                    e = e.strip()
                    if e:
                        examples.append(e)

            # add to grouped 
        grouped[item]["pinyin"] = pinyin
        grouped[item]["benzi"] = benzi
        grouped[item]["mean"].append([label, pos, definition] + examples)

    # output JSON file 
    result = [
        {
            "item": key,
            "pinyin": value["pinyin"],
            "benzi": value["benzi"],
            "mean": value["mean"]
        }
        for key, value in grouped.items()
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"JSON file is successfully built at: {output_path} ({len(result)} entries in total)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Input CSV path")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(__file__), "configs.toml"),
        help="Config TOML path",
    )
    args = parser.parse_args()
    csv_to_glossary_json(args.csv, args.out, args.config)
