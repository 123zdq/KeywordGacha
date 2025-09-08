
import threading
from dataclasses import dataclass, field
from typing import Any

from src.base.Base import TranslationStatus


@dataclass
class Item:
    # 默认值
    src: str = ""                                                 # 原文
    dst: str = ""                                                 # 译文
    name_src: str | list[str] | None = None                       # 角色姓名原文
    name_dst: str | list[str] | None = None                       # 角色姓名译文
    extra_field: str | dict[str, Any] = ""                        # 额外字段原文
    tag: str = ""                                                 # 标签
    row: int = 0                                                  # 行号
    status: TranslationStatus = TranslationStatus.UNTRANSLATED    # 翻译状态
    retry_count: int = 0                                          # 重试次数，当前只有单独重试的时候才增加此计数
    skip_internal_filter: bool = False                            # 跳过内置过滤器

    # 线程锁
    lock: threading.Lock = field(init=False, repr=False, compare=False, default_factory=threading.Lock)

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
    def get_name_src(self) -> str | list[str] | None:
        with self.lock:
            return self.name_src

    # 设置角色姓名原文
    def set_name_src(self, name_src: str | list[str] | None) -> None:
        with self.lock:
            self.name_src = name_src

    # 获取角色姓名译文
    def get_name_dst(self) -> str | list[str] | None:
        with self.lock:
            return self.name_dst

    # 设置角色姓名译文
    def set_name_dst(self, name_dst: str | list[str] | None) -> None:
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

    # 获取翻译状态
    def get_status(self) -> str:
        with self.lock:
            return self.status

    # 设置翻译状态
    def set_status(self, status: TranslationStatus) -> None:
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
