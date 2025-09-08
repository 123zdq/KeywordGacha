import re
from abc import ABC, abstractmethod
from pathlib import Path

from charset_normalizer import from_path as charset_normalizer_from_path

# from src.base.Base import Language
from module.Item import Item
from module.Text import TextBase
from src.base.Base import FileType, TextType
from src.module.Config import config


class File(ABC):
    def __init__(self, config: config) -> None:
        super().__init__()

        # 初始化
        self.config = config
        self.file_type: FileType = FileType.NONE                                     # 原始文件的类型
        self.file_path: Path = config.input_folder                                   # 原始文件的相对路径
        self.text_type: TextType = TextType.NONE                                     # 文本的实际类型
        self.input_path: Path = config.input_folder
        self.output_path: Path = config.output_folder
        # self.source_language: Language = config.source_language
        # self.target_language: Language = config.target_language
        self.items: list[Item] = []                                                  # 待翻译的文本条目

    @abstractmethod
    def read_from_path(self, abs_path: Path) -> list[Item]:
        pass

    # 获取文件编码
    @staticmethod
    def get_encoding(path: str, add_sig_to_utf8: bool = True) -> str:
        encoding: str = "utf-8"

        try:
            encoding = charset_normalizer_from_path(path).best().encoding
        except Exception:
            pass

        # utf-8 是 ascii 的严格超集
        # 所以如果检测到 ascii 可视为 utf-8
        if encoding == "ascii":
            encoding = "utf-8"

        # 如果需要添加 BOM 标识
        if add_sig_to_utf8 and (encoding == "utf_8" or encoding == "utf-8"):
            encoding = "utf-8-sig"

        return encoding


    # 文本类型检查
    # WOLF
    REGEX_WOLF: tuple[re.Pattern[str], re.Pattern[str]] = (
        re.compile(r"@\d+", flags=re.IGNORECASE),                                    # 角色 ID
        re.compile(r"\\[cus]db\[.+?:.+?:.+?\]", flags=re.IGNORECASE),                # 数据库变量 \cdb[0:1:2]
    )

    # RENPY
    CJK_RANGE: str = rf"{TextBase.CJK_RANGE}{TextBase.HANGUL_RANGE}{TextBase.HIRAGANA_RANGE}{TextBase.KATAKANA_RANGE}"
    REGEX_RENPY: tuple[re.Pattern[str], re.Pattern[str]] = (
        re.compile(r"\{[^\{" + CJK_RANGE + r"]*?\}", flags=re.IGNORECASE),           # {w=2.3}
        re.compile(r"\[[^\[" + CJK_RANGE + r"]*?\]", flags=re.IGNORECASE),           # [renpy.version_only]
    )

    # RPGMaker
    REGEX_RPGMaker: tuple[re.Pattern[str], re.Pattern[str], re.Pattern[str]] = (
        re.compile(r"en\(.{0,8}[vs]\[\d+\].{0,16}\)", flags=re.IGNORECASE),          # en(!s[982]) en(v[982] >= 1)
        re.compile(r"if\(.{0,8}[vs]\[\d+\].{0,16}\)", flags=re.IGNORECASE),          # if(!s[982]) if(v[982] >= 1)
        re.compile(r"[/\\][a-z]{1,8}[<\[][a-z\d]{0,16}[>\]]", flags=re.IGNORECASE),  # /c[xy12] \bc[xy12] \bc<xy12>
    )

    # 判断实际的文本类型 WOLF / RPGMAKER / RENPY
    @classmethod
    def text_type_check(cls, src: str) -> TextType:
        if any(p.search(src) for p in cls.REGEX_WOLF):
            return TextType.WOLF
        elif any(p.search(src) for p in cls.REGEX_RPGMaker):
            return TextType.RPGMAKER
        elif any(p.search(src) for p in cls.REGEX_RENPY):
            return TextType.RENPY
        return TextType.NONE

    def auto_select_text_type(self) -> None:
        # 如果文件类型是 XLSX、TRANS、KVJSON、MESSAGEJSON，且没有文本类型，则判断实际的文本类型 WOLF / RPGMAKER / RENPY
        if self.file_type in (FileType.XLSX, FileType.TRANS, FileType.KVJSON, FileType.MESSAGEJSON) and self.text_type == TextType.NONE:
            for item in self.items:
                self.text_type = self.text_type_check(item.get_src())
                if self.text_type != TextType.NONE:
                    break

