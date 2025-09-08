import json
import os
import re
from pathlib import Path
from typing import Any

import openpyxl
import openpyxl.worksheet.worksheet

from module.Item import Item
from module.Text import CJK, JA, KO, Latin
from src.base.Base import TranslationStatus
from src.model.NER import NER
from src.model.Word import Word
from src.module.Config import config
from src.module.File.ASS import ASS
from src.module.File.EPUB import EPUB
from src.module.File.KVJSON import KVJSON
from src.module.File.MD import MD
from src.module.File.MESSAGEJSON import MESSAGEJSON
from src.module.File.RENPY import RENPY
from src.module.File.SRT import SRT
from src.module.File.TRANS.TRANS import TRANS
from src.module.File.TXT import TXT
from src.module.File.WOLFXLSX import WOLFXLSX
from src.module.File.XLSX import XLSX
from src.module.LogManager import LogManager
from src.module.Normalizer import Normalizer
from src.module.XLSXHelper import XLSXHelper

LogHelper = LogManager.get()


class FileManager:

    # 去重
    RE_DUPLICATE = re.compile(r"[\r\n]+")

    # 除了空格以外的行内空白符
    RE_NON_SPACE_WHITESPACE = re.compile(r"[^\S ]+")

    # 一个或多个连续的空格
    RE_MULTIPLE_SPACES = re.compile(r" +")

    def __init__(self) -> None:
        super().__init__()

    # 加载角色数据
    @staticmethod
    def load_names(path: str) -> tuple[dict[int, str], dict[int, str]]:
        names: dict[int, str] = {}
        nicknames: dict[int, str] = {}

        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as reader:
                for item in json.load(reader):
                    if isinstance(item, dict):
                        id = item.get("id", -1)

                        if not isinstance(id, int):
                            continue

                        names[id] = item.get("name", "")
                        nicknames[id] = item.get("nickname", "")
            LogHelper.info(
                f"从 [green]Actors.json[/] 文件中加载了 {len(names) + len(nicknames)} 条数据，稍后将执行 [green]角色代码还原[/] 步骤 ..."
            )

        return names, nicknames

    # 清理文本
    @classmethod
    def cleanup(cls, line: str, language: int) -> str:
        # 由于上面的代码移除，可能会产生空人名框的情况，干掉
        line = line.replace("【】", "")

        # 干掉除了空格以外的行内空白符（包括换行符、制表符、回车符、换页符等）
        line = cls.RE_NON_SPACE_WHITESPACE.sub("", line)

        # 合并连续的空格为一个空格
        line = cls.RE_MULTIPLE_SPACES.sub(" ", line)

        return line

    # 检索并处理输入文件
    # TODO: 重新组织底层文件处理器
    @staticmethod
    def read_from_path(input_path: str) -> list[str]:
        items: list[Item] = []
        paths: list[str] = []

        # 检索输入路径下的所有文件
        try:
            if os.path.isfile(input_path):
                paths = [input_path]
            elif os.path.isdir(input_path):
                for root, _, files in os.walk(input_path):
                    paths.extend([f"{root}/{file}".replace("\\", "/") for file in files])
        except Exception as e:
            LogHelper.error("输入文件检索失败 ...", e)

        # 依次解析每个输入文件
        try:

            # 文件注册表  小写扩展名 -> ((处理器类名表),[对应的文件表])
            handler_map: dict[str, tuple[tuple[Any, ...], list[str]]] = {
                ".md": ((MD,), []),
                ".txt": ((TXT,), []),
                ".ass": ((ASS,), []),
                ".srt": ((SRT,), []),
                ".epub": ((EPUB,), []),
                ".xlsx": ((XLSX, WOLFXLSX,),[],),
                ".rpy": ((RENPY,), []),
                ".trans": ((TRANS,), []),
                ".json": ((KVJSON, MESSAGEJSON,),[],),
            }

            # 伪数据
            # config: dict[str, str] = {"input_folder": "", "output_folder": "", "source_language": "", "target_language": ""}
            cg=config()
            cg.input_folder=Path(input_path)

            # 文件分发与处理
            for path in paths:
                _, ext = os.path.splitext(path)
                ext = ext.lower()
                if ext in handler_map:
                    handler_map[ext][1].append(path)
                else:
                    LogHelper.debug(f"已跳过不支持的文件格式: {path}")
            for ext in handler_map.values():
                for handler in ext[0]:
                    for path in ext[1]:
                        items.extend(handler(cg).read_from_path(Path(path)))
        except Exception as e:
            LogHelper.error("输入文件解析失败 ...", e)

        return [
            v.get_src().strip()
            for v in items
            if (
                v.get_src().strip() != ""
                # and (v.get_file_type() == FileType.TRANS or v.get_status() != TranslationStatus.EXCLUDED)
                and (v.get_status() != TranslationStatus.EXCLUDED)
            )
        ]

    # 从输入文件中加载数据
    def read_lines_from_input_file(self, input_path: str, language: int) -> tuple[list[str], dict[int, str], dict[int, str]]:
        self.input_path = input_path

        # 依次读取每个数据文件
        with LogHelper.status("正在读取输入文件 ..."):
            lines = self.read_from_path(self.input_path)

        LogHelper.info(f"已在 [green]{self.input_path}[/] 路径下找到数据 [green]{len(lines)}[/] 条")

        # 尝试从输入路径的同级路径或者下级路径加载角色数据，找不到则生成伪数据
        names, nicknames = {}, {}
        if os.path.isfile(f"{self.input_path}/Actors.json"):
            names, nicknames = self.load_names(f"{self.input_path}/Actors.json")
        elif os.path.isfile(f"{os.path.dirname(self.input_path)}/Actors.json"):
            names, nicknames = self.load_names(f"{os.path.dirname(self.input_path)}/Actors.json")

        # 依次读取每个数据文件
        with LogHelper.status("正在检查输入文件 ..."):

            lines_filtered: list[str] = []
            for line in lines:
                line = Normalizer.normalize(line)
                line: str = self.cleanup(line, language)

                if len(line) == 0:
                    continue

                if language == NER.Language.ZH and not CJK.any(line):
                    continue
                elif language == NER.Language.EN and not Latin.any(line):
                    continue
                elif language == NER.Language.JA and not JA.any(line):
                    continue
                elif language == NER.Language.KO and not KO.any(line):
                    continue

                # 添加结果
                lines_filtered.append(line)
        LogHelper.info(f"已读取到文本 {len(lines)} 行，其中有效文本 {len(lines_filtered)} 行 ...")

        return lines_filtered, names, nicknames

    # 将 词语日志 写入文件
    @staticmethod
    def write_log_to_file(words: list[Word], path: str, language: int) -> None:
        with open(path, "w", encoding="utf-8") as writer:
            for k, word in enumerate(words):
                if getattr(word, "surface", "") != "":
                    writer.write(f"词语原文 : {word.surface}" + "\n")

                if getattr(word, "score", 0.0) >= 0:
                    writer.write(f"置信度 : {word.score:.4f}" + "\n")

                if getattr(word, "surface_romaji", "") != "":
                    writer.write(f"罗马音 : {word.surface_romaji}" + "\n")

                if getattr(word, "count", 0) >= 0:
                    writer.write(f"出现次数 : {word.count}" + "\n")

                if getattr(word, "surface_translation", "") != "":
                    writer.write(f"词语翻译 : {word.surface_translation}" + "\n")

                if getattr(word, "gender", "") != "":
                    writer.write(f"角色性别 : {word.gender}" + "\n")

                if getattr(word, "context_summary", "") != "":
                    writer.write(f"语义分析 : {word.context_summary}" + "\n")

                if len(getattr(word, "context", [])) > 0:
                    writer.write("参考文本原文 : ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※" + "\n")
                    writer.write(f"{word.get_context_str_for_translate(language)}" + "\n")

                if len(getattr(word, "context_translation", [])) > 0:
                    writer.write("参考文本翻译 : ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※" + "\n")
                    writer.write(f"{FileManager.RE_DUPLICATE.sub("\n", "\n".join(word.context_translation))}" + "\n")

                # 多写入一个换行符，确保每段信息之间有间隔
                writer.write("\n")

        LogHelper.info(f"结果已写入 - [green]{path}[/]")

    # 写入文件
    def write_glossary_to_json_file(self, words: list[Word], path: str, language: int) -> None:
        with open(path, "w", encoding="utf-8") as file:
            datas = []
            for word in words:
                data = {}
                data["src"] = word.surface
                data["dst"] = word.surface_translation

                if word.group == "角色" and "男" in word.gender:
                    data["info"] = "男性"
                elif word.group == "角色" and "女" in word.gender:
                    data["info"] = "女性"
                elif word.group == "角色":
                    data["info"] = "名字"
                else:
                    data["info"] = f"{word.group}"

                datas.append(data)

            file.write(json.dumps(datas, indent=4, ensure_ascii=False))
            LogHelper.info(f"结果已写入 - [green]{path}[/]")

    # 写入文件
    def write_glossary_to_xlsx_file(self, words: list[Word], path: str, language: int) -> None:
        # 新建工作表
        book: openpyxl.Workbook = openpyxl.Workbook()
        sheet: openpyxl.worksheet.worksheet.Worksheet = book.active

        # 设置表头
        sheet.column_dimensions["A"].width = 32
        sheet.column_dimensions["B"].width = 32
        sheet.column_dimensions["C"].width = 32
        sheet.column_dimensions["D"].width = 32
        XLSXHelper.set_cell_value(sheet, 1, 1, "src", 10)
        XLSXHelper.set_cell_value(sheet, 1, 2, "dst", 10)
        XLSXHelper.set_cell_value(sheet, 1, 3, "info", 10)
        XLSXHelper.set_cell_value(sheet, 1, 4, "regex", 10)

        # 将数据写入工作表
        for row, word in enumerate(words):
            if word.group == "角色" and "男" in word.gender:
                info = "男性"
            elif word.group == "角色" and "女" in word.gender:
                info = "女性"
            elif word.group == "角色":
                info = "名字"
            else:
                info = word.group

            XLSXHelper.set_cell_value(sheet, row + 2, 1, word.surface, 10)
            XLSXHelper.set_cell_value(sheet, row + 2, 2, word.surface_translation, 10)
            XLSXHelper.set_cell_value(sheet, row + 2, 3, info, 10)
            XLSXHelper.set_cell_value(sheet, row + 2, 4, "False", 10)

        # 保存工作簿
        book.save(path)
        LogHelper.info(f"结果已写入 - [green]{path}[/]")

    # 将结果写入文件
    def write_result_to_file(self, output_path: str, words: list[Word], language: int) -> None:
        # 获取输出路径
        os.makedirs(output_path, exist_ok=True)
        file_name, _ = os.path.splitext(os.path.basename(self.input_path))

        # 清理一下
        [os.remove(entry.path) for entry in os.scandir(output_path) if entry.is_file() and f"{file_name}_" in entry.path]

        for group in {word.group for word in words}:
            words_by_type = [word for word in words if word.group == group]

            # 检查数据有效性
            if len(words_by_type) == 0:
                continue

            # 写入文件
            prefix = f"{output_path}/{file_name}_{group}"
            self.write_log_to_file(words_by_type, f"{prefix}_日志.txt", language)
            self.write_glossary_to_json_file(words_by_type, f"{prefix}_术语表.json", language)
            self.write_glossary_to_xlsx_file(words_by_type, f"{prefix}_术语表.xlsx", language)
