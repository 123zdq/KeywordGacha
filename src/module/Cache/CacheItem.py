import re
import threading
from dataclasses import dataclass, field
from typing import Any, ClassVar

from module.Text import TextBase

# import tiktoken
# import tiktoken_ext
# from tiktoken_ext import openai_public
from src.base.Base import FileType, TextType, TranslationStatus


@dataclass
class CacheItem:
    # 必须显式的引用这两个库，否则打包后会报错
    # tiktoken_ext
    # openai_public

    # 缓存 Token 数量
    TOKEN_COUNT_CACHE: ClassVar[dict[str, int]] = {}

    # WOLF
    REGEX_WOLF: ClassVar[tuple[re.Pattern[str], re.Pattern[str]]] = (
        re.compile(r"@\d+", flags=re.IGNORECASE),                      # 角色 ID
        re.compile(r"\\[cus]db\[.+?:.+?:.+?\]", flags=re.IGNORECASE),  # 数据库变量 \cdb[0:1:2]
    )

    # RENPY
    CJK_RANGE: ClassVar[str] = rf"{TextBase.CJK_RANGE}{TextBase.HANGUL_RANGE}{TextBase.HIRAGANA_RANGE}{TextBase.KATAKANA_RANGE}"
    REGEX_RENPY: ClassVar[tuple[re.Pattern[str], re.Pattern[str]]] = (
        re.compile(r"\{[^\{" + CJK_RANGE + r"]*?\}", flags=re.IGNORECASE),  # {w=2.3}
        re.compile(r"\[[^\[" + CJK_RANGE + r"]*?\]", flags=re.IGNORECASE),  # [renpy.version_only]
    )

    # RPGMaker
    REGEX_RPGMaker: ClassVar[tuple[re.Pattern[str], re.Pattern[str], re.Pattern[str]]] = (
        re.compile(r"en\(.{0,8}[vs]\[\d+\].{0,16}\)", flags=re.IGNORECASE),          # en(!s[982]) en(v[982] >= 1)
        re.compile(r"if\(.{0,8}[vs]\[\d+\].{0,16}\)", flags=re.IGNORECASE),          # if(!s[982]) if(v[982] >= 1)
        re.compile(r"[/\\][a-z]{1,8}[<\[][a-z\d]{0,16}[>\]]", flags=re.IGNORECASE),  # /c[xy12] \bc[xy12] \bc<xy12>
    )

    # 默认值
    src: str = ""                                         # 原文
    dst: str = ""                                         # 译文
    name_src: str | tuple[str] = None                     # 角色姓名原文
    name_dst: str | tuple[str] = None                     # 角色姓名译文
    extra_field: str | dict[str, Any] = ""                # 额外字段原文
    tag: str = ""                                         # 标签
    row: int = 0                                          # 行号
    file_type: FileType = FileType.NONE                   # 原始文件的类型
    file_path: str = ""                                   # 原始文件的相对路径
    text_type: str = TextType.NONE                        # 文本的实际类型
    status: str = TranslationStatus.UNTRANSLATED          # 翻译状态
    retry_count: int = 0                                  # 重试次数，当前只有单独重试的时候才增加此计数
    skip_internal_filter: bool = False                    # 跳过内置过滤器

    # 线程锁
    lock: threading.Lock = field(init=False, repr=False, compare=False, default_factory=threading.Lock)

    def __post_init__(self) -> None:
        # 如果文件类型是 XLSX、TRANS、KVJSON、MESSAGEJSON，且没有文本类型，则判断实际的文本类型 WOLF / RPGMAKER / RENPY
        if self.file_type in (FileType.XLSX, FileType.TRANS, FileType.KVJSON, FileType.MESSAGEJSON) and self.text_type == TextType.NONE:
            if any(p.search(self.src) for p in CacheItem.REGEX_WOLF):
                self.text_type = TextType.WOLF
            elif any(p.search(self.src) for p in CacheItem.REGEX_RPGMaker):
                self.text_type = TextType.RPGMAKER
            elif any(p.search(self.src) for p in CacheItem.REGEX_RENPY):
                self.text_type = TextType.RENPY

    # 获取原文
    def get_src(self) -> str:
        with self.lock:
            # print(self.src)
            # input()
            return self.src

    # 设置原文
    def set_src(self, src: str) -> None:
        with self.lock:
            self.src = src

    # 获取译文
    def get_dst(self) -> str:
        with self.lock:
            return self.dst

    # 设置译文
    def set_dst(self, dst: str) -> None:
        with self.lock:
            self.dst = dst

            # 有时候模型的回复反序列化以后会是 int 等非字符类型，所以这里要强制转换成字符串
            # TODO:可能需要更好的处理方式
            # if isinstance(dst, str):
            #     self.dst = dst
            # else:
            #     self.dst = str(dst)

    # 获取角色姓名原文
    def get_name_src(self) -> str | tuple[str]:
        with self.lock:
            return self.name_src

    # 设置角色姓名原文
    def set_name_src(self, name_src: str | tuple[str]) -> None:
        with self.lock:
            self.name_src = name_src

    # 获取角色姓名译文
    def get_name_dst(self) -> str | tuple[str]:
        with self.lock:
            return self.name_dst

    # 设置角色姓名译文
    def set_name_dst(self, name_dst: str | tuple[str]) -> None:
        with self.lock:
            self.name_dst = name_dst

    # 获取额外字段原文
    def get_extra_field(self) -> str | dict:
        with self.lock:
            return self.extra_field

    # 设置额外字段原文
    def set_extra_field(self, extra_field: str | dict) -> None:
        with self.lock:
            self.extra_field = extra_field

    # 获取标签
    def get_tag(self) -> str:
        with self.lock:
            return self.tag

    # 设置标签
    def set_tag(self, tag: str) -> None:
        with self.lock:
            self.tag = tag

    # 获取行号
    def get_row(self) -> int:
        with self.lock:
            return self.row

    # 设置行号
    def set_row(self, row: int) -> None:
        with self.lock:
            self.row = row

    # 获取文件类型
    def get_file_type(self) -> str:
        with self.lock:
            return self.file_type

    # 设置文件类型
    def set_file_type(self, type: str) -> None:
        with self.lock:
            self.file_type = type

    # 获取文件路径
    def get_file_path(self) -> str:
        with self.lock:
            return self.file_path

    # 设置文件路径
    def set_file_path(self, path: str) -> None:
        with self.lock:
            self.file_path = path

    # 获取文本类型
    def get_text_type(self) -> str:
        with self.lock:
            return self.text_type

    # 设置文本类型
    def set_text_type(self, type: str) -> None:
        with self.lock:
            self.text_type = type

    # 获取翻译状态
    def get_status(self) -> str:
        with self.lock:
            return self.status

    # 设置翻译状态
    def set_status(self, status: str) -> None:
        with self.lock:
            self.status = status

    # 获取重试次数
    def get_retry_count(self) -> int:
        with self.lock:
            return self.retry_count

    # 设置重试次数
    def set_retry_count(self, retry_count: int) -> None:
        with self.lock:
            self.retry_count = retry_count

    # 获取跳过内置过滤器
    def get_skip_internal_filter(self) -> bool:
        with self.lock:
            return self.skip_internal_filter

    # 设置跳过内置过滤器
    def set_skip_internal_filter(self, skip_internal_filter: bool) -> None:
        with self.lock:
            self.skip_internal_filter = skip_internal_filter

    # （已弃用）获取 Token 数量
    """
    def get_token_count(self) -> int:
        with self.lock:
            if self.src not in CacheItem.TOKEN_COUNT_CACHE:
                CacheItem.TOKEN_COUNT_CACHE[self.src] = len(tiktoken.get_encoding("o200k_base").encode(self.src))
            return CacheItem.TOKEN_COUNT_CACHE[self.src]
    """
