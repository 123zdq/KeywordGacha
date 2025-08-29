import bisect
import json
import os
import re


from pecab import PeCab
from sudachipy import Dictionary


from model.Word import Word
from module.Text.TextHelper import TextHelper
from module.LogManager import LogManager

LogHelper = LogManager.get()
from module.ProgressHelper import ProgressHelper
from model.kg_ner_model import NER_SERVER


class NER:
    # 语言模式
    class Language:
        ZH = 100
        EN = 200
        JA = 300
        KO = 400

    # 片段长度
    MAX_LENGTH = NER_SERVER.MAX_LENGTH

    # 伪名列表
    FAKE_NAME = [
        "蓝霁云",  # 雨后初晴的意象
        "檀秋萦",  # 檀香与秋思萦绕
        "墨临川",  # 文墨与临水意境
        "泠鸢晚",  # 清越之声与黄昏纸鸢
        "云螭遥",  # 云雾中的龙形
        "邝溟幽",  # 深邃幽暗的海域
        "颛鹤唳",  # 鹤鸣九皋的悠远
        "玄璆夜",  # 黑玉般的夜色
        "砚秋辞",  # 文房与秋意的结合
        "聆音澈",  # 聆听清澈之音
        "雪渟寒",  # 积雪静潭的寒意
        "萤照晚",  # 萤火照亮黄昏
        "青霭浮",  # 青色云雾漂浮
        "绛霄临",  # 红色天空降临
        "墨漪澜",  # 墨色水波荡漾
        "霜序遥",  # 霜降时节的遥远
        "霁川流",  # 雨后天晴的河流
        "檀烟渺",  # 檀香烟雾渺茫
        "玄螭隐",  # 黑龙隐匿
        "青冥远",  # 青色天空的遥远
        "墨笙寒",  # 墨色笙箫的寒意
        "霜序晚",  # 霜降时节的黄昏
        "霁云舒",  # 雨后天晴的云舒展
        "檀香凝",  # 檀香凝结
        "玄夜阑",  # 深夜将尽
        "紫陌迁",  # 紫色田陌，有迁移之感
        "容止安",  # 容貌举止安详
        "蔚迟暮",  # 蔚蓝与迟暮之年
        "靖远尘",  # 安靖远离尘世
        "聆夜笙",  # 聆听夜晚笙歌
        "绯辞镜",  # 绯红辞别镜子
        "予怀瑾",  # 给予怀抱美玉
        "疏星朗",  # 稀疏星星明朗
        "霁无瑕",  # 雨后晴朗无瑕疵
        "素问筠",  # 素雅询问竹筠
        "景行瞻",  # 高尚品行值得瞻仰
        "聆风吟",  # 聆听风的吟唱
        "怀霜澈",  # 怀抱冰霜般清澈
        "静姝窈",  # 静美女子窈窕
        "思覃远",  # 思绪深远
        "语凝烟",  # 话语凝结如烟
        "霁月朗",  # 雨后明月清朗
        "星河澹",  # 星河景象恬淡
        "清芷蘅",  # 清雅芬芳的白芷和杜蘅
        "韶华倾",  # 美好年华倾注
        "霁雪霏",  # 雨后雪花纷飞
        "云舒卷",  # 云朵舒卷自如
        "風祭宵",  # 风祭祀的夜晚
        "月代雫",  # 月亮替代的滴落
        "雨宮静",  # 雨宫的宁静
        "星影律",  # 星星影子的规律
        "霧島朔",  # 雾岛的朔日
        "時雨遥",  # 时雨的遥远
        "雪村茜",  # 雪村的茜草色
        "花垣葵",  # 花园墙壁边的葵
        "水瀬碧",  # 水流湍急处的碧蓝
        "空木凪",  # 空心树的平静
        "音羽奏",  # 音羽的演奏
        "琴引紬",  # 琴弦牵引的丝绸
        "篝火茜",  # 篝火的茜草色
        "砂川凪",  # 砂石河流的平静
        "藤咲雫",  # 藤花盛开时滴落
        "柚木碧",  # 柚子树的碧蓝
        "柊木律",  # 冬青树的规律
        "楓原宵",  # 枫树原野的夜晚
        "霞見遥",  # 从霞雾中眺望远方
        "篝屋静",  # 篝火屋的宁静
        "草薙朔",  # 草薙的朔日
        "月詠茜",  # 咏唱月亮的茜草色
        "風早奏",  # 风快速的演奏
        "雪代紬",  # 雪替代的丝绸
        "花散里",  # 花朵散落的村庄
        "鸦羽透",  # 乌鸦羽毛意象的透明感
        "星屑海",  # 天文与海洋的浪漫结合
        "铁仙斎",  # 金属质感的三字姓氏
        "龙胆朔",  # 植物名与朔日的组合
        "冬月葵",  # 冬季月色与葵花的结合
        "胧月夜",  # 朦胧月色的夜晚
        "霞草雫",  # 霞光与草间露珠的意象
        "薄墨葵",  # 淡墨色与葵花的结合
        "绯桜咲",  # 绯色樱花盛开的意象
        "苍海凪",  # 苍茫大海与风平浪静的组合
        "翠岚悠",  # 翠绿山岚与悠远意境的结合
        "琥珀川",  # 宝石与河流的意象组合
        "霁辰砂",  # 雨后晴朗，辰砂般红艳
        "暮云合",  # 傍晚云彩汇合
        "清漪岚",  # 清澈水波，山岚缥缈
        "素影瞳",  # 素净身影，清澈眼眸
        "怀瑾瑜",  # 怀抱美玉瑾瑜
        "朗夜汐",  # 明朗夜晚，潮汐涨落
        "轻尘陌",  # 轻微尘埃，田间小路
        "雪霁空",  # 雪后晴朗天空
        "泠然止",  # 清冷的样子，停止
        "澹台清",  # 复姓澹台，清澈之意
        "汐見凪",  # 眺望海潮的平静
        "氷川朔",  # 冰川的朔日
        "月白静",  # 月亮白色般的宁静
        "風音律",  # 风的声音的规律
        "雪華遥",  # 雪花的遥远
        "雨夜雫",  # 雨夜的滴落
    ]

    # 各语言分词器
    SUDACHI = Dictionary().create()  # 日文
    PECAB = PeCab()  # 韩文

    # 预编译正则表达式
    # 名词表 英
    PATTERN_1 = re.compile(r"\b(.+?)\b")
    # 代码转名
    PATTERN_2 = re.compile(r"\\n\[(\d+)\]", flags=re.IGNORECASE)
    PATTERN_3 = re.compile(r"\\nn\[(\d+)\]", flags=re.IGNORECASE)
    # 匹配姓名框
    PATTERN_4 = re.compile(r"【(.*?)】")

    # NER黑名单
    BLACKLIST: set[str] = set()

    def __init__(self) -> None:
        super().__init__()
        self.ner = NER_SERVER()

    # 加载NER黑名单文件内容  默认检查 blacklist 文件夹中的所有 .json 文件
    @classmethod
    def load_blacklist(cls) -> None:
        try:
            for entry in os.scandir("blacklist"):
                if entry.is_file() and entry.name.endswith(".json"):
                    with open(entry.path, "r", encoding="utf-8-sig") as reader:
                        for v in json.load(reader):
                            if v.get("srt") != None:
                                cls.BLACKLIST.add(v.get("srt"))
        except Exception as e:
            LogHelper.error("加载NER黑名单配置文件时发生错误", e)

    # 生成片段
    def generate_chunks(self, input_lines: list[str], chunk_size: int) -> tuple[list[str], list[int], list[int]]:
        n: int = len(input_lines)

        chunks: list[str] = []
        chunks2lines: list[int] = []
        line_start_id: list[int] = [-1] * n

        chunk_length = 0
        chunk_include: list[str] = []
        next_id: int = 0
        for i, line in enumerate(input_lines):
            # from transformers.tokenization_utils_base import BatchEncoding
            # https://huggingface.co/docs/transformers/v4.55.4/en/internal/tokenization_utils#transformers.PreTrainedTokenizerBase.__call__
            length: int = int(self.ner.tokenizer(line, padding=False, truncation=True, max_length=chunk_size - 3, return_length=True)["length"][0])  # type: ignore

            if chunk_length + length > chunk_size - 3:
                # DEBUG
                if chunk_length <= 0:
                    LogHelper.error(f"NER - 分块构造算法错误 - chunk_length 值异常1: {chunk_length}")

                chunks.append("\n".join(chunk_include))
                chunks2lines.append(next_id)

                chunk_length = 0
                chunk_include = []
                next_id = i

            line_start_id[i] = chunk_length
            chunk_length += length + 1
            chunk_include.append(line)

        # 循环结束后添加最后一段
        if len(chunk_include) > 0:
            # DEBUG
            if chunk_length <= 0:
                LogHelper.error(f"NER - 分块构造算法错误 - chunk_length 值异常2: {chunk_length}")

            chunks.append("\n".join(chunk_include))
            chunks2lines.append(next_id)

        chunks2lines.append(n)
        # DEBUG
        if len(chunks2lines) != len(chunks) + 1:
            LogHelper.error(f"NER - 分块构造算法错误 -  分块数异常: {len(chunks2lines)} && {len(chunks)}")
        return chunks, chunks2lines, line_start_id

    # 生成词语
    @classmethod
    def generate_words(
        cls, text: str, line: str, nouns: dict[str, int] | None, score: float, group: str, language: int, input_lines: list[str]
    ) -> list[Word]:
        words: list[Word] = []

        # 生成名词表
        if nouns is None:
            # DEBUG
            LogHelper.error("NER - 分块算法错误 - 名词表丢失")
            nouns = cls.generate_nouns(line, language)

        # 生成词语列表
        # 当文本为英文且包含 ' 时不拆分，避免误拆复合短语
        # 当文本为中文时，使用包含空格的拆分规则
        # 否则使用不包含空格的拆分规则
        if language == cls.Language.EN and "'" in text:
            surfaces = [text]
        else:
            surfaces = [
                stripped
                for v in TextHelper.split_by_punctuation(text, (language in (cls.Language.ZH, cls.Language.JA)))
                if (stripped := v.strip()) != ""
            ]

        # 遍历词语
        for surface in surfaces:
            # 按语言移除首尾无效字符
            surface = cls.strip_by_language(surface, language)

            # 跳过显示长度小于等于2的词语
            if TextHelper.get_display_length(surface) <= 2:
                continue

            # 按语言验证词语
            if cls.verify_by_language(surface, language) == False:
                continue

            # 根据名词表对词语进行修正
            surface = cls.fix_by_noun_set(surface, line, nouns, language)

            word = Word()
            word.count = 1
            word.score = score
            word.surface = surface
            word.group = group
            word.input_lines = input_lines
            word.context.append(line)
            words.append(word)
        return words

    # 生成名词表
    # TODO: 需重新确认 “词频” 概念的精确定义  英文实现可能不精确,标点会被提出  未对于中文实现
    @classmethod
    def generate_nouns(cls, line: str, language: int) -> dict[str, int]:
        nouns = {}

        # 英
        if language == cls.Language.EN:
            nouns = {surface: line.count(surface) for surface in cls.PATTERN_1.findall(line)}

        # 日
        elif language == cls.Language.JA:
            # 获取名词表
            for token in cls.SUDACHI.tokenize(line):
                # 获取表面形态
                surface = token.surface()
                # 跳过包含至少一个标点符号的条目
                if TextHelper.any_punctuation(surface):
                    continue
                # 跳过目标类型以外的条目
                if not any(v in ",".join(token.part_of_speech()) for v in ("地名", "人名", "名詞")):
                    continue
                nouns[surface] = line.count(surface)

        # 韩
        elif language == cls.Language.KO:
            nouns: dict[str, int] = {surface: line.count(surface) for surface in cls.PECAB.nouns(line)}

        return nouns

    # 根据名词表修正词语
    @classmethod
    def fix_by_noun_set(cls, text: str, line: str, nouns: dict[str, int], language: int) -> str:
        # 中文无名词表 不修
        if language not in (cls.Language.EN, cls.Language.JA, cls.Language.KO):
            return text

        def fix_single_text(text: str) -> str:
            lc = line.count(text)
            for noun, count in nouns.items():
                if lc == count and len(text) < len(noun) and text in noun:
                    return noun
            return text

        if " " not in text:
            text = fix_single_text(text)
        else:
            splited = text.split(" ")
            splited[0] = fix_single_text(splited[0])
            splited[-1] = fix_single_text(splited[-1])
            text = " ".join(splited)
        return text

    # 按语言移除首尾无效字符  未知语言时返回原串
    @classmethod
    def strip_by_language(cls, text: str, language: int) -> str:
        if language == cls.Language.ZH:
            return TextHelper.CJK.strip_non_target(text).strip("的")

        if language == cls.Language.EN:
            return TextHelper.Latin.strip_non_target(text).removeprefix("a ").removeprefix("an ").removeprefix("the ").strip()

        if language == cls.Language.JA:
            return TextHelper.JA.strip_non_target(text).strip("の")

        if language == cls.Language.KO:
            return TextHelper.KO.strip_non_target(text)

        return text

    # 按语言进行验证  未知语言时返回True
    @classmethod
    def verify_by_language(cls, text: str, language: int) -> bool:
        if text.lower() in cls.BLACKLIST:
            return False
        if language == cls.Language.ZH:
            return TextHelper.CJK.any(text)
        if language == cls.Language.EN:
            # 首字母小写则False
            if not text[0].isupper():
                return False
            return TextHelper.Latin.any(text)
        if language == cls.Language.JA:
            return TextHelper.JA.any(text)
        if language == cls.Language.KO:
            return TextHelper.KO.any(text)
        return True

    # 查找 Token 所在的行
    # 已弃用该函数
    def get_line_by_offset(self, text: str, lines: list[str], offsets: list[tuple[int]], start: int, end: int) -> str:
        result = ""

        # 当实体词语位于行的末尾时，会将换行符的长度也计入起止位置，所以要 end 要 -1
        if text != "" and text[-1] == " ":
            end = end - 1

        for line, offset in zip(lines, offsets):
            if start >= offset[0] and end <= offset[1]:
                result = line
                break

        return result

    # 代码转换为姓名   例如 角色代码 \N[123] -> 姓名  并统计新转的姓名集
    @classmethod
    def code_to_name(
        cls, line: str, names: dict[int, str], nicknames: dict[int, str], fake_name_mapping: dict[str, str]
    ) -> tuple[str, set[str]]:
        surfaces: set[str] = set()

        def repl(match: re.Match[str], names: dict[int, str]) -> str:
            # 索引在范围内则替换，不在范围内则原文返回
            fname: str | None = names.get(int(match.group(1)), "")
            if fname == "":
                name = match.group(0).lower()
                if (fname := fake_name_mapping.get(name, None)) is None:
                    if len(cls.FAKE_NAME) > 0:
                        fname = cls.FAKE_NAME.pop()
                        fake_name_mapping[name] = fname
                    else:
                        # DEBUG
                        LogHelper.error("NER - 假名表耗尽")
                        return match.group(0)
            surfaces.add(fname)
            return fname

        # 根据 actors 中的数据还原 角色代码 \N[123] 实际指向的名字
        line = cls.PATTERN_2.sub(lambda match: repl(match, names), line)
        # 根据 actors 中的数据还原 角色代码 \NN[123] 实际指向的名字
        line = cls.PATTERN_3.sub(lambda match: repl(match, nicknames), line)
        return line, surfaces

    # 查找实体词语
    # TODO: 考虑是否需要在该步结束后将假名池复原
    def search_for_entity(
        self, input_lines: list[str], names: dict[int, str], nicknames: dict[int, str], language: int
    ) -> tuple[list[Word], dict[str, str]]:
        words: list[Word] = []
        line_nouns: list[dict[str, int]] = []

        """
        if language == self.Language.JA:
            self.sudachi = Dictionary().create()
        elif language == self.Language.KO:
            self.pecab = PeCab()
            # warnings.filterwarnings("ignore", message="overflow encountered in scalar add")
        """

        LogHelper.print("")
        with LogHelper.status("正在对文本进行预处理 ..."):
            seen: set[str] = set()
            fake_name_mapping: dict[str, str] = {}
            for i, line in enumerate(input_lines):
                # 代码转换为姓名
                line, surfaces = self.code_to_name(line, names, nicknames, fake_name_mapping)
                input_lines[i] = line

                # 匹配姓名框
                for surface in self.PATTERN_4.findall(line):
                    if TextHelper.get_display_length(surface) <= 16:
                        surfaces.add(surface)

                # 生成名词表
                line_nouns.append(self.generate_nouns(line, language))

                # 筛选并添加
                for surface in surfaces:
                    for word in self.generate_words(surface, line, line_nouns[i], self.ner.SCORE_INF, "PER", language, input_lines):
                        seen.add(word.surface)
                        words.append(word)

            # 切割文本
            chunks, chunks2lines, line_start_id = self.generate_chunks(input_lines, self.MAX_LENGTH)

        with ProgressHelper.get_progress() as progress:
            self.ner.start()
            pid = progress.add_task("查找实体词语", total=None)
            for i, result in enumerate(self.ner.classifier((v for v in chunks), batch_size=self.ner.bacth_size)):
                # 处理 NER模型 识别结果
                for token in result:
                    text = token.get("word")
                    index = bisect.bisect_right(line_start_id, token.get("start"), lo=chunks2lines[i], hi=chunks2lines[i + 1])
                    # DEBUG
                    if index == 0:
                        LogHelper.error("NER - 分块算法构造错误 - 二分查找失败")
                        index = 1
                    score = token.get("score")
                    entity_group = token.get("entity_group")
                    words.extend(
                        self.generate_words(text, input_lines[index - 1], line_nouns[index - 1], score, entity_group, language, input_lines)
                    )
                progress.update(pid, advance=1, total=len(chunks))
            self.ner.debug_cuda_memory_info()
            self.ner.release()
            self.ner.debug_cuda_memory_info()

        # 打印通过模式匹配抓取的角色实体
        LogHelper.print("")
        LogHelper.info(f"[查找实体词语] 已完成 ...")
        if len(seen) > 0:
            fake_name_mapping_ex = {v: k for k, v in fake_name_mapping.items()}
            surfaces = [fake_name_mapping_ex.get(surface, surface) for surface in seen]
            LogHelper.info(f"[查找实体词语] 通过 [green]模式匹配[/] 抓取到角色实体 - {", ".join(surfaces)}")

        return words, fake_name_mapping
