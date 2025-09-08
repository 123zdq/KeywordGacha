import re
from unicodedata import east_asian_width as unicodedata_east_asian_width


class TextHelper:

    # 汉字标点符号（CJK）
    CJK_PUNCTUATION_SET = {
        chr(char)
        for start, end in (
            (0x3001, 0x303F),  # CJK标点（排除全角空格0x3000）
            (0xFF01, 0xFF0F),  # 全角标点（！＂＃＄％＆＇（）＊＋，－．／）
            (0xFF1A, 0xFF1F),  # 全角标点（：；＜＝＞？）
            (0xFF3B, 0xFF40),  # 全角标点（［＼］＾＿｀）
            (0xFF5B, 0xFF65),  # 全角标点（｛｜｝～｟｠）
            (0xFFE0, 0xFFEE),  # 补充全角符号（￠￡￢￣￤￨等）
        )
        for char in range(start, end + 1)
    }

    # 拉丁标点符号
    LATIN_PUNCTUATION_SET = {
        chr(char)
        for start, end in (
            (0x0021, 0x002F),  # 基本拉丁标点（!"#$%&'()*+,-./）  排除半角空格
            (0x003A, 0x0040),  # 基本拉丁标点（:;<=>?@）
            (0x005B, 0x0060),  # 基本拉丁标点（[\]^_`）
            (0x007B, 0x007E),  # 基本拉丁标点（{|}~）
            (0x2000, 0x206F),  # 通用标点符号（含引号、破折号等）
            (0x2E00, 0x2E7F),  # 补充标点符号（双引号、括号等）
            (0x2010, 0x2027),  # 连字符、破折号、引号等
            (0x2030, 0x205E),  # 千分比符号、引号等
        )
        for char in range(start, end + 1)
    }

    # 特殊符号(不属于标点符号范围但是当作标点符号处理)
    SPECIAL_PUNCTUATION_SET = {
        chr(0x00B7),  # ·
        chr(0x30FB),  # ・
        chr(0x2665),  # ♥
    }

    PUNCTUATION_SET = CJK_PUNCTUATION_SET | LATIN_PUNCTUATION_SET | SPECIAL_PUNCTUATION_SET

    # 预编译正则表达式
    PATTERN = re.compile(r"^\d+|\d+$")  # 匹配开头或结尾的阿拉伯数字

    # 判断一个字符是否是标点符号
    @classmethod
    def is_punctuation(cls, char: str) -> bool:
        # return cls.is_cjk_punctuation(char) or cls.is_latin_punctuation(char) or cls.is_special_punctuation(char)
        return char in cls.PUNCTUATION_SET

    # 判断一个字符是否是汉字标点符号
    @classmethod
    def is_cjk_punctuation(cls, char: str) -> bool:
        return char in cls.CJK_PUNCTUATION_SET

    # 判断一个字符是否是拉丁标点符号
    @classmethod
    def is_latin_punctuation(cls, char: str) -> bool:
        return char in cls.LATIN_PUNCTUATION_SET

    # 判断一个字符是否是特殊标点符号
    @classmethod
    def is_special_punctuation(cls, char: str) -> bool:
        return char in cls.SPECIAL_PUNCTUATION_SET

    # 判断输入的字符串是否包含至少一个标点符号
    @classmethod
    def any_punctuation(cls, text: str) -> bool:
        return any(cls.is_punctuation(char) for char in text)

    # 判断输入的字符串是否全部为标点符号  空串为 True
    @classmethod
    def all_punctuation(cls, text: str) -> bool:
        return all(cls.is_punctuation(char) for char in text)

    # 移除开头结尾的标点符号  O(n)
    @classmethod
    def strip_punctuation(cls, text: str) -> str:
        text = text.strip()
        if not text:
            return text
        start, end = 0, len(text) - 1
        while start <= end and cls.is_punctuation(text[start]):
            start += 1
        if start > end:
            return ""
        while end > start and cls.is_punctuation(text[end]):
            end -= 1
        return text[start : end + 1]

    # 移除开头结尾的阿拉伯数字
    @classmethod
    def strip_arabic_numerals(cls, text: str) -> str:
        return cls.PATTERN.sub("", text)

    # 按标点符号分割字符串
    @classmethod
    def split_by_punctuation(cls, text: str, split_by_space: bool) -> list[str]:
        result: list[str] = []
        current_segment: list[str] = []
        for char in text:
            if cls.is_punctuation(char) or (split_by_space and char in (chr(0x0020), chr(0x3000))):
                if current_segment != []:
                    result.append("".join(current_segment))
                    current_segment = []
            else:
                current_segment.append(char)
        if current_segment != []:
            result.append("".join(current_segment))
        return result

    # 计算字符串的实际显示长度
    @staticmethod
    def get_display_length(text: str) -> int:
        # unicodedata.east_asian_width(c) 返回字符 c 的东亚洲宽度属性。
        # NaH 表示窄（Narrow）、中立（Neutral）和半宽（Halfwidth）字符，这些字符通常被认为是半角字符。
        # 其他字符（如全宽字符）的宽度属性为 W 或 F，这些字符被认为是全角字符。
        return sum(1 if unicodedata_east_asian_width(c) in "NaH" else 2 for c in text)

    # 计算 Jaccard 相似度  O(n+m)  空串与空串的相似度为 0.0
    # TODO: 可考虑 n-gram Jaccard  以考察频率与顺序
    @staticmethod
    def check_similarity_by_jaccard(x: str, y: str) -> float:
        set_x = set(x)
        set_y = set(y)

        # 求交集
        intersection = len(set_x & set_y)

        # 求并集
        union = len(set_x) - intersection + len(set_y)

        # 计算并返回相似度，完全一致是 1，完全不同是 0
        return intersection / union if union > 0 else 0.0
