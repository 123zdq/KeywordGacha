# 简介



本项目是基于 [KeywordGacha v0.14.0](https://github.com/neavo/KeywordGacha/tree/b1379be69a6b4d06d5e00b5a551cbb7350feadd3) 的二次开发版本，旨在保留核心特性并增强自动化体验

### 主要变化（相对原项目v0.14）
v0.14.2
* 自动化：增强了配置文件，移除了运行时所需的键盘输入
* 优化：适配引导解码技术（支持的后端：vllm、llama.cpp），现在本地模型会 **严格地遵循格式** 来回应词义分析任务



# 使用

0. 将 `config.json` 复制一份并重命名为 `config_private.json`

1. 按需编辑 `config_private.json` 文件

2. 将需要处理的文本放入 `input` 文件夹

3. 运行 `python app.py` 

4. 等待程序运行结束，从 `output` 文件夹取出结果



# 说明

* `config.json` 同时作为 默认配置 和 配置文档，不建议直接修改

* git 会忽略 `config_private.json`，以防止在自动更新时丢失配置

* 配置生效优先级：`config_private.json` $>$ `config.json`

* 假设后端为兼容 openAI 协议的 LLM 服务器

* `config_private.json` 只需包含与 `config.json` 不同的项

`config_private.json` 的一个填写样例：

```json
{
    "base_url": [
        "http://192.168.5.147:11451/v1",
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
