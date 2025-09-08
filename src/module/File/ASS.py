from pathlib import Path

from module.Item import Item
from src.base.Base import FileType
from src.module.File.FileHandler import File


class ASS(File):
    # [Script Info]
    # ; This is an Advanced Sub Station Alpha v4+ script.
    # Title:
    # ScriptType: v4.00+
    # PlayDepth: 0
    # ScaledBorderAndShadow: Yes

    # [V4+ Styles]
    # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
    # Style: Default,Arial,20,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,10,1

    # [Events]
    # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    # Dialogue: 0,0:00:08.12,0:00:10.46,Default,,0,0,0,,にゃにゃにゃ
    # Dialogue: 0,0:00:14.00,0:00:15.88,Default,,0,0,0,,えーこの部屋一人で使\Nえるとか最高じゃん
    # Dialogue: 0,0:00:15.88,0:00:17.30,Default,,0,0,0,,えるとか最高じゃん

    # 读取
    def read_from_path(self, abs_path: Path) -> list[Item]:
        self.file_type = FileType.ASS
        self.file_path = abs_path.relative_to(self.input_path)  # 获取相对路径

        # 数据处理
        with abs_path.open(encoding=self.get_encoding(str(abs_path))) as reader:
            self.lines = reader.readlines()
            lines = [line.strip() for line in self.lines]  # 按照换行符来分行并去除每行首尾空白字符

            # 格式字段的数量
            in_event = False
            format_field_num = -1
            for line in lines:
                # 判断是否进入事件块
                if line == "[Events]":
                    in_event = True
                # 在事件块中寻找格式字段
                if in_event and line.startswith("Format:"):
                    format_field_num = len(line.split(",")) - 1
                    break

            for i, line in enumerate(lines):
                if not line.startswith("Dialogue:"):
                    continue
                content = ",".join(line.split(",")[format_field_num:])
                if content == "":
                    continue
                extra_field = self.lines[i].replace(content, "{{CONTENT}}")
                # 添加数据
                content = content.replace("\\N", "\n")
                self.items.append(
                    Item(
                        src=content,
                        dst=content,
                        extra_field=extra_field,
                        row=i,
                    )
                )

        return self.items

    # 写入
    def write_to_path(self, items: list[Item]) -> None:
        lines = self.lines.copy() if self.config.deduplication_in_bilingual else self.lines
        for item in items:
            lines[item.row] = item.get_extra_field().replace("{{CONTENT}}", item.get_dst().replace("\n", "\\N"))

        abs_path = self.output_path / self.file_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with abs_path.open("w", encoding="utf-8") as writer:
            writer.write("".join(lines))

        if not self.config.deduplication_in_bilingual:
            return
        # 处理双语文件
        for item in items:
            self.lines[item.row] = item.get_extra_field().replace(
                "{{CONTENT}}", f"{item.get_src().replace('\n', '\\N')}\\N{item.get_dst().replace('\n', '\\N')}"
            )
        bp = abs_path.parent / "bilingual" / abs_path.name
        bp.parent.mkdir(parents=True, exist_ok=True)
        with bp.open("w", encoding="utf-8") as writer:
            writer.write("".join(self.lines))
