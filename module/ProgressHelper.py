from typing import Any

from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn


class ProgressHelper:
    # 获取一个进度条实例
    @staticmethod
    def get_progress(**kwargs: Any) -> Progress:
        return Progress(
            TextColumn("{task.description}", justify="right"),
            "•",
            BarColumn(bar_width=None),
            "•",
            TextColumn("{task.completed}/{task.total}", justify="right"),
            "•",
            TimeElapsedColumn(),
            "/",
            TimeRemainingColumn(),
            **kwargs,
        )
