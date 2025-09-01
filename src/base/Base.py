from enum import IntEnum, StrEnum


# 文件类型
class FileType(StrEnum):
    NONE = "NONE"                                # 无类型
    MD = "MD"                                    # .md Markdown
    TXT = "TXT"                                  # .txt 文本文件
    SRT = "SRT"                                  # .srt 字幕文件
    ASS = "ASS"                                  # .ass 字幕文件
    EPUB = "EPUB"                                # .epub
    XLSX = "XLSX"                                # .xlsx Translator++ SExtractor
    WOLFXLSX = "WOLFXLSX"                        # .xlsx WOLF 官方翻译工具导出文件
    RENPY = "RENPY"                              # .rpy RenPy
    TRANS = "TRANS"                              # .trans Translator++
    KVJSON = "KVJSON"                            # .json MTool
    MESSAGEJSON = "MESSAGEJSON"                  # .json SExtractor

# 实际文本类型
class TextType(StrEnum):
    NONE = "NONE"                                # 无类型，即纯文本
    MD = "MD"                                    # Markdown
    KAG = "KAG"                                  # KAG 游戏文本
    WOLF = "WOLF"                                # WOLF 游戏文本
    RENPY = "RENPY"                              # RENPY 游戏文本
    RPGMAKER = "RPGMAKER"                        # RPGMAKER 游戏文本

# 翻译状态
class TranslationStatus(StrEnum):
    UNTRANSLATED = "UNTRANSLATED"                # 待翻译
    TRANSLATING = "TRANSLATING"                  # 翻译中
    TRANSLATED = "TRANSLATED"                    # 已翻译
    TRANSLATED_IN_PAST = "TRANSLATED_IN_PAST"    # 过去已翻译
    EXCLUDED = "EXCLUDED"                        # 已排除
    DUPLICATED = "DUPLICATED"                    # 重复条目

# 接口格式
class APIFormat(StrEnum):
    OPENAI = "OpenAI"
    GOOGLE = "Google"
    ANTHROPIC = "Anthropic"
    SAKURALLM = "SakuraLLM"

# 事件
class Event(IntEnum):
    PLATFORM_TEST_DONE = 100                     # API 测试完成
    PLATFORM_TEST_START = 101                    # API 测试开始
    TRANSLATION_START = 200                      # 翻译开始
    TRANSLATION_STOP = 210                       # 翻译停止
    TRANSLATION_STOP_DONE = 220                  # 翻译停止完成
    TRANSLATION_UPDATE = 230                     # 翻译状态更新
    TRANSLATION_MANUAL_EXPORT = 240              # 翻译结果手动导出
    CACHE_FILE_AUTO_SAVE = 300                   # 缓存文件自动保存
    PROJECT_STATUS = 400                         # 项目状态检查
    PROJECT_STATUS_CHECK_DONE = 410              # 项目状态检查完成
    APP_UPDATE_CHECK = 500                       # 检查更新
    APP_UPDATE_CHECK_DONE = 510                  # 检查更新 - 完成
    APP_UPDATE_DOWNLOAD = 520                    # 检查更新 - 下载
    APP_UPDATE_DOWNLOAD_UPDATE = 530             # 检查更新 - 下载进度更新
    APP_UPDATE_EXTRACT = 540                     # 检查更新 - 解压
    APP_TOAST_SHOW = 600                         # 显示 Toast
    GLOSSARY_REFRESH = 700                       # 术语表刷新
    APP_SHUT_DOWN = 1000                         # 应用关闭

# 任务状态
class Status(IntEnum):
    IDLE = 100                                   # 无任务
    TESTING = 200                                # 运行中
    TRANSLATING = 300                            # 运行中
    STOPPING = 400                               # 停止中

# 接口格式
class ToastType(StrEnum):
    INFO = "INFO"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
