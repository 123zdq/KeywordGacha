from pathlib import Path


class config:
    def __init__(self) -> None:
        self.input_folder: Path = Path(".")
        self.output_folder: Path = Path(".")
        self.deduplication_in_bilingual = True  # 是否额外输出双语字幕
