import gc
import logging

import torch
from transformers import pipeline
from transformers.models.modernbert.configuration_modernbert import ModernBertConfig
from transformers.models.modernbert.modeling_modernbert import ModernBertForTokenClassification
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
from transformers.pipelines.token_classification import TokenClassificationPipeline

from module.LogManager import LogManager


class NER_SERVER:
    MODEL_PATH = "resource/kg_ner_bf16"
    MAX_LENGTH = 512  # 与 NER.py 中的该值保持一致
    SCORE_INF = 65535  # 提词结果 SCORE 值的上界

    def __init__(self) -> None:
        super().__init__()

        self.logger: LogManager = LogManager.get()
        # 设置日志过滤器
        logging.getLogger("transformers.pipelines.base").filter = lambda record: "Device set to use" not in record.msg

        self.gpu_boost = torch.cuda.is_available()
        self.bacth_size = 32 if self.gpu_boost else 1

        # 加载分词器
        self.tokenizer: PreTrainedTokenizerFast = PreTrainedTokenizerFast.from_pretrained(
            self.MODEL_PATH,
            model_max_length=self.MAX_LENGTH,
            local_files_only=True,
            padding="max_length",
            truncation=True,
            max_length=self.MAX_LENGTH,
        )

    # 加载显存资源
    def start(self) -> None:
        if self.gpu_boost:
            self.logger.info("检测到有效的 [green]GPU[/] 环境，已启用 [green]GPU[/] 加速 ...")
        else:
            self.logger.warning("未检测到有效的 [green]GPU[/] 环境，无法启用 [green]GPU[/] 加速 ...")

        # 根据配置选择使用数据类型
        if self.gpu_boost:
            # transformers.utils.import_utils.is_torch_bf16_gpu_available()
            torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        else:
            torch_dtype = torch.float32

        # 创建配置，并关闭 reference_compile
        config: ModernBertConfig = ModernBertConfig.from_pretrained(
            self.MODEL_PATH,
            local_files_only=True,
        )
        config.reference_compile = False

        device: str = "cuda" if self.gpu_boost else "cpu"

        # 加载模型
        self.model: ModernBertForTokenClassification = ModernBertForTokenClassification.from_pretrained(
            self.MODEL_PATH,
            config=config,
            attn_implementation="sdpa",
            torch_dtype=torch_dtype,
            local_files_only=True,
        )
        self.model.to(device=device)

        # 加载分类器
        self.classifier: TokenClassificationPipeline = pipeline(
            "token-classification",
            model=self.model,
            device=device,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )

    # 释放显存资源
    def release(self) -> None:
        del self.model
        del self.classifier
        gc.collect()
        if self.gpu_boost:
            torch.cuda.empty_cache()

    def debug_cuda_memory_info(self) -> None:
        self.logger.debug(f"显存保留量 - {torch.cuda.memory_reserved()/1024/1024:>8.2f} MB")
        self.logger.debug(f"显存分配量 - {torch.cuda.memory_allocated()/1024/1024:>8.2f} MB")
