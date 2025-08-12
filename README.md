# 简介



本项目是基于 [KeywordGacha v0.14.0](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3) 的二次开发版本，旨在保留核心特性并增强自动化体验

v0.14.1
* 增强了 配置文件、命令行模式
* 移除了 ~~运行时所需的键盘输入~~



# 关于原项目

[KeywordGacha](https://github.com/neavo/KeywordGacha) 自 [V0.20](https://github.com/neavo/KeywordGacha/releases/tag/MANUAL_BUILD_v0.20.2) 起，不再适配 **纯本地工作流**

* [V0.20](https://github.com/neavo/KeywordGacha/releases/tag/MANUAL_BUILD_v0.20.2)
* * 基于原生 AI 技术 的全新 KeywordGacha
* * 16种语言，全格式接口
* * 最佳实践： **全流程地使用各厂商的旗舰LLM**，本地不需要硬件算力

* [V0.14](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3)
* * 实现：先用作者自训练的 [实体识别模型NER](https://huggingface.co/neavo/keyword_gacha_multilingual_ner) 提词，再转发至 LLM 做语义分析，对 LLM 的能力（即尺寸）需求不高
* * 中、英、日、韩
* * 最佳实践：与 本地 LLM + [LinguaGacha翻译器](https://github.com/neavo/LinguaGacha) 配合



# 快速开始

1. 编辑 `config.json` 文件，填写 LLM 服务器的 api 信息

2. 将需要处理的文本放入 `input` 文件夹

3. 运行 `app.exe` 

4. 等待程序运行结束，从 `output` 文件夹取出结果文件



# 使用说明

优先级：**命令行 > 配置文件**

## 配置文件

```json
{
    "api_key": [
        "no_key_required",
        "接口密钥，从接口平台方获取，使用在线接口时一定要设置正确。"
    ],
    "base_url": [
        "http://192.168.5.20:11451/v1",
        "请求地址，从接口平台方获取，使用在线接口时一定要设置正确。"
    ],
    "model_name": [
        "Qwen3",
        "模型名称，从接口平台方获取，使用在线接口时一定要设置正确。"
    ],
    "count_threshold": [
        3,
        "出现次数阈值，出现次数低于此值的词语会被过滤掉以节约时间。"
    ],
    "request_timeout": [
        240,
        "网络请求超时时间，如果频繁出现 timeout 字样的网络错误，可以调大这个值。"
    ],
    "request_frequency_threshold": [
        32,
        "网络请求频率阈值，单位为 次/秒，值可以小于 1，如果频繁出现 429 代码的网络错误，可以调小这个值。",
        "使用 llama.cpp 运行的本地模型时，将根据 llama.cpp 的配置调整自动设置，无需手动调整这个值。",
        "使用 火山引擎 等不限制并发数的在线接口时可以调大这个值。"
    ],
    "context_translate_mode": [
        0,
        "是否翻译参考文本，0 - 不翻译，1 - 全部翻译，2 - 只翻译角色实体"
    ],
    "input": [
        "input",
        "输入文件夹路径，默认：当前目录下的 input 文件夹"
    ],
    "output": [
        "output",
        "输出文件夹路径，默认：当前目录下的 output 文件夹",
        "每次输出前会自动清除该文件夹下的所有旧文件！！！",
        "确保此项参数填写正确，否则可能会导致重要数据丢失！！！"
    ],
    "task": [
        3,
        "任务类型，1 - 中文文本，2 - 英文文本，3 - 日文文本，4 - 韩文文本，5 - 接口测试"
    ]
}
```

## 命令行

`app [-h] [--task 数字] [--input 输入文件夹路径]`

* `-h`, `--help`  显示帮助

* `--task`  任务类型，`1`表示中文文本，`2`表示英文文本，`3`表示日文文本，`4`表示韩文文本，`5`表示LLM接口测试

* `--input`  输入用的文件夹路径



# [特别说明](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3?tab=readme-ov-file#%E7%89%B9%E5%88%AB%E8%AF%B4%E6%98%8E-%EF%B8%8F)

- 如您在翻译过程中使用了 [KeywordGacha](https://github.com/neavo/KeywordGacha)，请在作品信息或发布页面的显要位置进行说明！
- 如您的项目涉及任何商业行为或者商业收益，在使用 [KeywordGacha](https://github.com/neavo/KeywordGacha) 前，请先与 [作者](github.com/neavo) 联系以获得授权！ 
