import os
import copy
import json
import asyncio
from types import SimpleNamespace

from pathlib import Path
import sys
# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich import box
from rich.table import Table
from rich.prompt import Prompt
from rich.traceback import install

from src.model.LLM import LLM
from src.model.NER import NER
from src.model.Word import Word
from src.module.LogManager import LogManager
from src.module.ProgressHelper import ProgressHelper
from src.module.TestHelper import TestHelper
from src.module.FileManager import FileManager

# import argparse
import time

start_time = time.time()

# 定义常量  实体词语的置信度阈值
SCORE_THRESHOLD = 0.60

LogHelper = LogManager.get()


# 格式化时间
def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)} 秒"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)} 分 {int(seconds)} 秒"
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)} 时 {int(minutes)} 分 {int(seconds)} 秒"


# 合并词语
def merge_words(words: list[Word]) -> list[Word]:
    words_unique: dict[str, Word] = {}
    for word in words:
        w = words_unique.get(word.surface)
        if w is None:
            words_unique[word.surface] = word
        else:
            w.score = min(0.9999, max(w.score, word.score))
    return list(words_unique.values())
    """
    for v in words_unique.values():
        word = v[0]
        word.score = min(0.9999, max(w.score for w in v))
        words_merged.append(word)
    
    # DEBUG 这里的所有count必然为1, 排序是多余的
    for v in words_merged:
        if v.count!=1:
            LogHelper.error("word.count 预期外行为")

    return sorted(words_merged, key=lambda x: x.count, reverse=True)
    """


# 搜索参考文本，并按出现次数排序
def search_for_context(words: list[Word], input_lines: list[str]) -> list[Word]:
    # 复制一份，避免后续的修改影响原始数据
    input_lines_ex = copy.copy(input_lines)

    # 按实体词语的长度降序排序
    words = sorted(words, key=lambda v: len(v.surface), reverse=True)

    LogHelper.print("")
    with ProgressHelper.get_progress() as progress:
        pid = progress.add_task("搜索参考文本", total=len(words))

        # 搜索参考文本
        for word in words:
            # 找出匹配的行
            index = {i for i, line in enumerate(input_lines_ex) if word.surface in line}

            # 获取匹配的参考文本，去重，并按长度降序排序
            word.context = list({line for i, line in enumerate(input_lines) if i in index})
            word.context = sorted(word.context, key=lambda v: len(v), reverse=True)
            word.count = len(word.context)
            word.group = "未知类型"

            # 掩盖已命中的实体词语文本，避免其子串错误的与父串匹配
            input_lines_ex = [
                line.replace(word.surface, len(word.surface) * "#") if i in index else line for i, line in enumerate(input_lines_ex)
            ]

            # 更新进度条
            progress.update(pid, advance=1)
    LogHelper.print("")

    # 按出现次数降序排序
    return sorted(words, key=lambda x: x.count, reverse=True)


# 按置信度过滤词语
def filter_words_by_score(words: list[Word], threshold: float) -> list[Word]:
    return [word for word in words if word.score >= threshold]


# 按出现次数过滤词语
def filter_words_by_count(words: list[Word], threshold: float) -> list[Word]:
    return [word for word in words if word.count >= max(1, threshold)]


# 获取指定类型的词
def get_words_by_type(words: list[Word], group: str) -> list[Word]:
    return [word for word in words if word.group == group]


# 移除指定类型的词
def remove_words_by_type(words: list[Word], group: str) -> list[Word]:
    return [word for word in words if word.group != group]


# 开始处理文本
async def process_text(llm: LLM, ner: NER, file_manager: FileManager, config: SimpleNamespace, language: int) -> None:
    # start_time = time.time()

    # 初始化
    words = []

    # 读取输入文件
    input_lines, names, nicknames = file_manager.read_lines_from_input_file(config.input, language)

    # 查找实体词语
    LogHelper.info("即将开始执行 [查找实体词语] ...")
    words, fake_name_mapping = ner.search_for_entity(input_lines, names, nicknames, language)

    # 合并相同词条
    words = merge_words(words)

    # 调试功能
    # TestHelper.check_score_threshold(words, "log/log_score_threshold.log")

    # 置信度阈值过滤
    LogHelper.info(f"即将开始执行 [置信度阈值]，当前置信度的阈值为 {SCORE_THRESHOLD:.4f} ...")
    words = filter_words_by_score(words, SCORE_THRESHOLD)
    LogHelper.info("[置信度阈值] 已完成 ...")

    # 搜索参考文本
    LogHelper.info("即将开始执行 [搜索参考文本] ...")
    words = search_for_context(words, input_lines)

    # 出现次数阈值过滤
    LogHelper.info(f"即将开始执行 [出现次数阈值]，当前出现次数的阈值为 {config.count_threshold} ...")
    words = filter_words_by_count(words, config.count_threshold)
    LogHelper.info("[出现次数阈值] 已完成 ...")

    # 设置 LLM 对象
    llm.set_language(language)
    # llm.set_request_limiter()

    # 等待 词义分析 任务结果
    LogHelper.info("即将开始执行 [词义分析] ...")
    words = await llm.surface_analysis_batch(words, fake_name_mapping)
    words = remove_words_by_type(words, "")

    # 调试功能
    TestHelper.save_surface_analysis_log(words, "logs/log_surface_analysis.log")
    TestHelper.check_result_duplication(words, "logs/log_result_duplication.log")

    # 等待 参考文本翻译 任务结果
    if language != NER.Language.ZH and config.context_translate_mode != 0:
        if config.context_translate_mode == 2:
            groups = ("角色",)
        elif config.context_translate_mode == 1:
            groups = {word.group for word in words}

        # 翻译参考文本
        for group in groups:
            LogHelper.info(f"即将开始执行 [参考文本翻译 - {group}] ...")
            word_by_group = get_words_by_type(words, group)
            word_by_group = await llm.context_translate_batch(word_by_group)

    # 还原伪名
    for word in words:
        for k, v in fake_name_mapping.items():
            word.context_summary = word.context_summary.replace(v, k)
            word.context = [line.replace(v, k) for line in word.context]
            word.context_translation = [line.replace(v, k) for line in word.context_translation]

    # 调试功能
    TestHelper.save_context_translate_log(words, "logs/log_context_translate.log")

    # 将结果写入文件
    LogHelper.info("将结果写入文件中 ...")
    file_manager.write_result_to_file(config.output, words, language)

    # 结束
    LogHelper.info(f"\n工作流程已结束，耗时 {format_duration(time.time() - start_time)} ，请检查输出的数据文件 ...")


# 接口测试
async def test_api(llm: LLM) -> None:
    # 设置请求限制器
    # llm.set_request_limiter()

    # 等待接口测试结果
    if await llm.api_test():
        LogHelper.print("")
        LogHelper.info("接口测试 [green]执行成功[/] ...")
    else:
        LogHelper.print("")
        LogHelper.warning("接口测试 [red]执行失败[/], 程序中止, 请检查配置文件 ...")
        sys.exit()

    LogHelper.print("")


# 打印应用信息
def print_app_info(config: SimpleNamespace, version: str) -> None:
    LogHelper.print("\n\n")
    LogHelper.rule(f"KeywordGacha {version}", style="light_goldenrod2")
    LogHelper.rule("[blue]https://github.com/123zdq/KeywordGacha", style="light_goldenrod2")
    LogHelper.rule("针对本地AI工作流优化的术语表生成工具", style="light_goldenrod2")
    LogHelper.print()

    table = Table(
        box=box.ASCII2,
        expand=True,
        highlight=True,
        show_lines=True,
        show_header=False,
        border_style="light_goldenrod2",
    )
    table.add_column("", style="white", ratio=2, overflow="fold")
    table.add_column("", style="white", ratio=5, overflow="fold")

    rows = []
    rows.append(("模型名称", str(config.model_name)))
    rows.append(("接口密钥", str(config.api_key)))
    rows.append(("接口地址", str(config.base_url)))
    rows.append(("网络请求超时时间", f"{config.request_timeout} 秒"))
    rows.append(("网络请求频率阈值", f"{config.request_frequency_threshold} 次/秒"))

    if config.context_translate_mode == 0:
        rows.append(("参考文本翻译模式", "不翻译"))
    elif config.context_translate_mode == 1:
        rows.append(("参考文本翻译模式", "翻译全部类型"))
    elif config.context_translate_mode == 2:
        rows.append(("参考文本翻译模式", "只翻译角色类型"))

    for row in rows:
        table.add_row(*row)
    LogHelper.print(table)

    LogHelper.print("请编辑 [green]config/config_private.json[/] 文件来修改上表中的设置\n")


# 打印菜单
# 此函数暂时弃用
def print_menu_main() -> int:
    LogHelper.print("请选择功能：")
    LogHelper.print("")
    LogHelper.print("\t--> 1. 开始处理 [green]中文文本[/]")
    LogHelper.print("\t--> 2. 开始处理 [green]英文文本[/]")
    LogHelper.print("\t--> 3. 开始处理 [green]日文文本[/]")
    LogHelper.print("\t--> 4. 开始处理 [green]韩文文本[/]")
    LogHelper.print("\t--> 5. 开始执行 [green]接口测试[/]")
    LogHelper.print("")
    choice = int(
        Prompt.ask(
            "请输入选项前的 [green]数字序号[/] 来使用对应的功能，默认为 [green][3][/] ",
            choices=["1", "2", "3", "4", "5"],
            default="3",
            show_choices=False,
            show_default=False,
        )
    )
    LogHelper.print("")

    return choice


# 主函数
async def begin(llm: LLM, ner: NER, file_manager: FileManager, config: SimpleNamespace, version: str) -> None:

    print_app_info(config, version)

    llm.set_request_limiter()

    if config.test_api:
        await test_api(llm)

    # choice = print_menu_main()
    if config.task == 1:
        await process_text(llm, ner, file_manager, config, NER.Language.ZH)
    elif config.task == 2:
        await process_text(llm, ner, file_manager, config, NER.Language.EN)
    elif config.task == 3:
        await process_text(llm, ner, file_manager, config, NER.Language.JA)
    elif config.task == 4:
        await process_text(llm, ner, file_manager, config, NER.Language.KO)


# 一些初始化步骤
def load_config() -> tuple[LLM, NER, FileManager, SimpleNamespace, str]:  # args: SimpleNamespace
    with LogHelper.status("正在初始化 [green]KG[/] 引擎 ..."):
        config = SimpleNamespace()
        version = ""

        try:
            # 优先使用开发环境配置文件
            if not os.path.isfile("config/config_dev.json"):
                path = "config/config.json"
            else:
                path = "config/config_dev.json"

            # 读取配置文件
            with open(path, "r", encoding="utf-8-sig") as reader:
                for k, v in json.load(reader).items():
                    setattr(config, k, v[0])

            # 读取私有配置文件
            with open("config/config_private.json", "r", encoding="utf-8-sig") as reader:
                for k, v in json.load(reader).items():
                    setattr(config, k, v[0])

            # 读取版本号文件
            with open("resource/version.txt", "r", encoding="utf-8-sig") as reader:
                version = reader.read().strip()
        except Exception as e:
            LogHelper.error("配置文件读取失败 ...", e)

        """
        # 如果有，用命令行参数覆盖配置文件中的设置
        for k, v in vars(args).items():
            if v != None:
                setattr(config, k, v)
        """

        # 初始化 LLM 对象
        llm = LLM(config)
        llm.load_prompt()
        llm.load_llm_config()

        # 初始化 NER 对象
        ner = NER()
        ner.load_blacklist()

        # 初始化 FileManager 对象
        file_manager = FileManager()

    return llm, ner, file_manager, config, version


# 确保程序出错时可以捕捉到错误日志
async def main() -> None:  # args: SimpleNamespace
    try:
        # 注册全局异常追踪器
        install()

        # 加载配置
        llm, ner, file_manager, config, version = load_config()  # args

        # 开始处理
        await begin(llm, ner, file_manager, config, version)
    except EOFError as e:
        LogHelper.error("EOFError - 程序即将退出 ...", e)
    except KeyboardInterrupt:
        LogHelper.error("KeyboardInterrupt - 程序即将退出 ...")
    except Exception as e:
        LogHelper.print()
        LogHelper.print()
        LogHelper.error("出现严重错误，程序即将退出，错误信息已保存至日志文件 [green]logs/app.log[/] ...", e)
        LogHelper.print()
        LogHelper.print()


# 入口函数
if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(prog="app")
    parser.add_argument(
        "--task",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="任务类型：1 - 中文文本，2 - 英文文本，3 - 日文文本，4 - 韩文文本，5 - 接口测试",
    )
    parser.add_argument("--input", type=str, help="输入文件夹")
    # parser.add_argument("--output", type=str, help="输出文件夹") # 前往 config.json 修改
    args = parser.parse_args()

    asyncio.run(main(args))
    """

    asyncio.run(main())
