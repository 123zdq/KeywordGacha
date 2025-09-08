import json
from pathlib import Path

import jsonschema

from module.Item import Item
from src.base.Base import FileType, TranslationStatus
from src.module.File.FileHandler import File


class KVJSON(File):
    # {
    #     "「あ・・」": "「あ・・」",
    #     "「ごめん、ここ使う？」": "「ごめん、ここ使う？」",
    #     "「じゃあ・・私は帰るね」": "「じゃあ・・私は帰るね」",
    # }
    SCHEMA = {
        "type": "object",
        "additionalProperties": {"type": "string"},
    }

    # 读取
    def read_from_path(self, abs_path: Path) -> list[Item]:
        self.file_type = FileType.KVJSON
        self.file_path = abs_path.relative_to(self.input_path)  # 获取相对路径

        json_data: dict[str, str] = {}
        # 格式校验
        try:
            with abs_path.open(encoding=self.get_encoding(str(abs_path))) as reader:
                json_data = json.load(reader)
            jsonschema.validate(json_data, self.SCHEMA)
        # 若格式不正确，默认返回0条数据
        except Exception:
            return []

        # 读取数据
        for i, (src, dst) in enumerate(json_data.items()):
            status: TranslationStatus = TranslationStatus.UNTRANSLATED
            if src == "":
                status = TranslationStatus.EXCLUDED
            elif dst != "" and src != dst:
                status = TranslationStatus.TRANSLATED_IN_PAST
            self.items.append(
                Item(
                    src=src,
                    dst=dst,
                    row=i,
                    status=status,
                )
            )

        return self.items

    # 写入
    def write_to_path(self, items: list[Item]) -> None:
        abs_path = self.output_path / self.file_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with abs_path.open("w", encoding="utf-8") as writer:
            writer.write(
                json.dumps(
                    {item.get_src(): item.get_dst() for item in items},
                    indent=4,
                    ensure_ascii=False,
                )
            )
