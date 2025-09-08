import json
from pathlib import Path

import jsonschema

from module.Item import Item
from src.base.Base import FileType, TextType
from src.module.File.FileHandler import File


class MESSAGEJSON(File):
    # [
    #     {
    #         "name": "",
    #         "message": "「同じ人類とは思えん」\r\n「それ」"
    #     },
    #     {
    #         "name": "虎鉄",
    #         "message": "それだけでは誰のことを言っているのか判然としないのに、\r\n誰のことを指しているのかは、一瞬で理解できてしまう。"
    #     },
    #     {
    #         "names": [],
    #         "message": "そこで注目を浴びているのは、\r\n星継\r\n銀音\r\n。\r\nこの学校でも随一の有名人で……俺の妹である。"
    #     },
    #     {
    #         "names": [
    #             "虎鉄",
    #             "銀音"
    #         ],
    #         "message": "華麗に踊る銀音。その周囲には、女子が大勢いて、\r\n手拍子をしたり、スマホのカメラを向けている。\r\n当然、その輪の外からも、多くの視線を集めていて――"
    #     },
    #     {
    #         "message": "「顔ちっさ。つか、ダンスうまくね？」\r\n「そりゃそーでしょ。かーっ、存在感やべー」\r\n「まずビジュアルが反則だよな。あの髪も含めて」"
    #     },
    # ]
    SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["message"],
            "properties": {
                "message": {"type": "string"},
                "name": {"type": "string"},
                "names": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "additionalProperties": False,
            "not": {"required": ["name", "names"]},  # name和names不同时出现
        },
    }

    # 读取
    def read_from_path(self, abs_path: Path) -> list[Item]:
        self.file_type = FileType.MESSAGEJSON
        self.text_type = TextType.KAG
        self.file_path = abs_path.relative_to(self.input_path)  # 获取相对路径

        json_data: list[dict[str, str | list[str]]] = []
        # 格式校验
        try:
            with abs_path.open(encoding=self.get_encoding(str(abs_path))) as reader:
                json_data = json.load(reader)
            jsonschema.validate(json_data, self.SCHEMA)
        # 若格式不正确，默认返回0条数据
        except Exception:
            return []

        for i, entry in enumerate(json_data):
            entry_message: str = entry["message"]
            name = entry.get("name")
            if name is None:
                name = entry.get("names")
            self.items.append(
                Item(
                    src=entry_message,
                    dst=entry_message,
                    name_src=name,
                    name_dst=name,
                    row=i,
                )
            )

        return self.items

    # TODO: 统一处理姓名字段
    def write_to_path(self, items: list[Item]) -> None:
        # 数据处理
        results: list[dict[str, str | list[str]]] = []
        for item in items:
            name = item.get_name_dst()
            result: dict[str, str | list[str]] = {"message": item.get_dst()}
            if name is not None:
                result["name" if isinstance(name, str) else "names"] = name
            results.append(result)
        # 写入
        abs_path = self.output_path / self.file_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with abs_path.open("w", encoding="utf-8") as writer:
            writer.write(
                json.dumps(
                    results,
                    indent=4,
                    ensure_ascii=False,
                )
            )
