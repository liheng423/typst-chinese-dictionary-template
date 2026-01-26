import csv
import json
import os
import sys
import logging
from typing import Dict
from typedef import GlossaryEntry

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import load_config_fields


logger = logging.getLogger(name=__name__)


def excel_to_glossary_json(csv_path, output_path, config_path) -> None:
    grouped: Dict[str, GlossaryEntry] = dict()
    fields = load_config_fields(
        config_path=config_path,
        section="csv",
        default=["item", "pinyin", "benzi", "label", "class", "meaning", "kangxi", "shuyu"],
    )

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="|")
        header = reader.fieldnames or []
        missing = [col for col in fields if col not in header]
        if missing:
            raise ValueError(f"CSV 缺少字段: {missing}")

        # 获取所有“示例”列名
        example_cols = [col for col in header if str(col).startswith("eg")]

        for row in reader:
            values = [str(row.get(col, "")).strip() for col in fields]
            item, pinyin, benzi, category, pos, definition, kangxi, shuyu = values

            # 收集所有非空示例
            examples = [
                str(row.get(col, "")).strip()
                for col in example_cols
                if str(row.get(col, "")).strip()
            ]

            if not pinyin:
                continue


            grouped[item]["pinyin"] = pinyin
            grouped[item]["benzi"] = benzi

            # 构造一个列表：分类、词性、释义 + 所有示例
            grouped[item]["mean"].append([category, pos, definition] + examples)


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

    print(f"JSON 文件已生成：{output_path}")


if __name__ == "__main__":
    excel_path = sys.argv[1] if len(sys.argv) > 2 else "./library/glossary.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "./library/glossary.json"
    config_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(__file__), "configs.toml"
    )
    excel_to_glossary_json(excel_path, output_path, config_path)
