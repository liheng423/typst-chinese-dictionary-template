import pandas as pd
import json
from collections import defaultdict
import sys

def excel_to_glossary_json(excel_path, output_path):
    df = pd.read_excel(excel_path)

    # 获取所有“示例”列名
    example_cols = [col for col in df.columns if str(col).startswith("eg")]

    grouped = defaultdict(lambda: {"pinyin": "", "benzi": "", "mean": []})

    for _, row in df.iterrows():
        item = str(row["item"]).strip()
        pinyin = str(row["pinyin"]).strip()
        benzi = str(row["benzi"]).strip()
        category = str(row["label"]).strip()
        pos = str(row["class"]).strip()
        definition = str(row["meaning"]).strip()
        kangxi = str(row["kangxi"]).strip()
        shuyu = str(row["shuyu"]).strip()

        kangxi_prefix = "【康熙字典节录】"
        shuyu_prefix = "【蜀语】"

        # 收集所有非空示例
        examples = [
    str(row[col]).strip()
    for col in example_cols
    if pd.notna(row[col]) and str(row[col]).strip()
        ]

        if len(examples) == 0:
            continue  # 必须至少有一个示例

        if kangxi != "nan": examples.append(kangxi_prefix + kangxi)
        if shuyu != "nan": examples.append(shuyu_prefix + shuyu)   


        grouped[item]["pinyin"] = pinyin
        grouped[item]["benzi"] = benzi

        # 构造一个列表：分类、词性、释义 + 所有示例
        grouped[item]["mean"].append(
            [category, pos, definition] + examples
        )


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

    print(f"✅ JSON 文件已生成：{output_path}")


if __name__ == "__main__":
    excel_path = sys.argv[1] if len(sys.argv) > 2 else "./library/glossary.xlsx"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "./library/glossary.json"
    excel_to_glossary_json(excel_path, output_path)