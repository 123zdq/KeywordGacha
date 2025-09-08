import os

from module.Item import Item
from src.base.Base import FileType


class TXT:

    def __init__(self, config: dict) -> None:
        super().__init__()

        # 初始化
        self.config: dict = config
        self.input_path: str = config.get("input_folder")
        self.output_path: str = config.get("output_folder")
        self.source_language: str = config.get("source_language")
        self.target_language: str = config.get("target_language")

    # 读取
    def read_from_path(self, abs_paths: list[str]) -> list[Item]:
        items:list[Item] = []
        for abs_path in abs_paths:
            # 获取相对路径
            try:
                rel_path = os.path.relpath(abs_path, self.input_path)
            except Exception:
                rel_path = abs_path

            # 数据处理
            with open(abs_path, encoding = "utf-8-sig") as reader:
                for line in [line.removesuffix("\n") for line in reader.readlines()]:
                    items.append(
                        Item({
                            "src": line,
                            "dst": line,
                            "row": len(items),
                            "file_type": FileType.TXT,
                            "file_path": rel_path,
                        })
                    )

        return items
