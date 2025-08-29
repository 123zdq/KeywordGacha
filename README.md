# 简介



本项目是基于 [KeywordGacha v0.14.0](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3) 的二次开发版本，旨在 **保留V14.0的核心特性** 并针对 **本地工作流** 增强自动化体验

### 主要变化
v0.14.2
* 增强了配置文件，移除了运行时所需的键盘输入
* （实验性支持）适配了引导解码
* * 支持的后端：vllm、llama.cpp

> 说明
与提示词的软限制不同，通过引导解码技术，遵循格式指令能力较差的本地小模型（例如Qwen3-30B）也能 **严格地遵循格式** 来回应词义分析任务

### to-do
* 分离 词义分析 与 术语翻译 任务
* 与 linguagacha 更加自动化地对接



# 快速开始

* 在 `config` 目录下，找到并复制一份 `config.json` ，将其重命名为 `config_private.json` 并按需编辑

* 将需要处理的文本放入 `input` 文件夹

* `python src/app.py`，等待处理结束 

* 从 `output` 文件夹取出结果



# 说明

* [支持的文本格式](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3?tab=readme-ov-file#%E6%96%87%E6%9C%AC%E6%A0%BC%E5%BC%8F-%EF%B8%8F) 与原版一致

* LLM接口：openAI 协议

* 生效优先级：`config/config_private.json` $>$ `config/config.json`

* `config.json` 既是 默认配置 也是 配置说明文档，不建议直接修改

* `config_private.json` 只需包含与默认配置 `config.json` 中不同的项即可
* git 不会追踪 `config_private.json`

一个 `config_private.json` 的样例如下：
```json
{
    "base_url": [
        "http://192.168.66.666:6666/v1",
        "请求地址，从接口平台方获取，使用在线接口时一定要设置正确。"
    ],
    "model_name": [
        "Qwen3",
        "模型名称，从接口平台方获取，使用在线接口时一定要设置正确。"
    ],
    "request_frequency_threshold": [
        32,
        "网络请求频率阈值，单位为 次/秒，值可以小于 1，如果频繁出现 429 代码的网络错误，可以调小这个值。",
        "使用 llama.cpp 运行的本地模型时，将根据 llama.cpp 的配置调整自动设置，无需手动调整这个值。",
        "使用 火山引擎 等不限制并发数的在线接口时可以调大这个值。"
    ]
}
```



# [特别说明](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3?tab=readme-ov-file#%E7%89%B9%E5%88%AB%E8%AF%B4%E6%98%8E-%EF%B8%8F)

- 如您在翻译过程中使用了 [KeywordGacha](https://github.com/neavo/KeywordGacha)，请在作品信息或发布页面的显要位置进行说明！
- 如您的项目涉及任何商业行为或者商业收益，在使用 [KeywordGacha](https://github.com/neavo/KeywordGacha) 前，请先与 [作者](https://github.com/neavo) 联系以获得授权！ 



# 关于原项目

[KeywordGacha](https://github.com/neavo/KeywordGacha) 自 [V0.20](https://github.com/neavo/KeywordGacha/releases/tag/MANUAL_BUILD_v0.20.2) 起，不再适配 **纯本地工作流**

* [V0.20](https://github.com/neavo/KeywordGacha/releases/tag/MANUAL_BUILD_v0.20.2)
* * 基于原生 AI 技术 的全新 KeywordGacha
* * 16种语言，全格式接口
* * 最佳实践： **全流程地使用各厂商的旗舰LLM**，本地不需要硬件算力

* [V0.14](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3)
* * 实现：先用作者自训练的 [NER模型](https://huggingface.co/neavo/keyword_gacha_multilingual_ner) 提词，再转发至 LLM 做语义分析，对 LLM 的能力（即尺寸）需求不高
* * 中、英、日、韩
* * 最佳实践：与 本地 LLM + [LinguaGacha翻译器](https://github.com/neavo/LinguaGacha) 配合
