import re
from pathlib import Path

from module.Item import Item
from src.base.Base import FileType, TextType, TranslationStatus
from src.module.File.FileHandler import File


class MD(File):
    # 添加图片匹配的正则表达式
    IMAGE_PATTERN = re.compile(r"!\[.*?\]\(.*?\)")

    # 读取
    def read_from_path(self, abs_path: Path) -> list[Item]:
        self.file_type = FileType.MD
        self.text_type = TextType.MD
        self.file_path = abs_path.relative_to(self.input_path)  # 获取相对路径

        # 数据处理
        with abs_path.open(encoding=self.get_encoding(str(abs_path))) as reader:
            lines = [line.removesuffix("\n") for line in reader.readlines()]
            in_code_block = False  # 跟踪是否在代码块内
            for i, line in enumerate(lines):
                # 检查是否进入或退出代码块
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                self.items.append(
                    Item(
                        src=line,
                        dst=line,
                        row=i,
                        status=TranslationStatus.EXCLUDED
                        if (in_code_block or MD.IMAGE_PATTERN.search(line))  # 如果是图片行或在代码块内，设置状态为 EXCLUDED
                        else TranslationStatus.UNTRANSLATED,
                    )
                )

        return self.items

    # 写入
    def write_to_path(self, items: list[Item]) -> None:
        abs_path = self.output_path / self.file_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with abs_path.open("w", encoding="utf-8") as writer:
            writer.write("\n".join([item.get_dst() for item in items]))
