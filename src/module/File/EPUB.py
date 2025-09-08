import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

from module.Item import Item
from src.base.Base import FileType
from src.module.File.FileHandler import File


class EPUB(File):
    # EPUB 文件中读取的标签范围
    EPUB_TAGS = ("p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "li", "td")

    # 读取
    def read_from_path(self, abs_path: Path) -> list[Item]:
        self.file_type = FileType.EPUB
        self.file_path = abs_path.relative_to(self.input_path)  # 获取相对路径

        # 数据处理
        with zipfile.ZipFile(abs_path, "r") as zip_reader:
            for path in zip_reader.namelist():
                if path.lower().endswith((".htm", ".html", ".xhtml")):
                    with zip_reader.open(path) as reader:
                        bs = BeautifulSoup(reader.read().decode("utf-8-sig"), "html.parser")
                        for dom in bs.find_all(self.EPUB_TAGS):
                            src: str = dom.get_text()
                            # 跳过空标签或嵌套标签
                            if src.strip() == "" or dom.find(self.EPUB_TAGS) is not None:
                                continue
                            self.items.append(Item(src=src, dst=src, tag=path, row=len(self.items)))
                elif path.lower().endswith(".ncx"):
                    with zip_reader.open(path) as reader:
                        bs = BeautifulSoup(reader.read().decode("utf-8-sig"), "lxml-xml")
                        for dom in bs.find_all("text"):
                            src: str = dom.get_text()
                            # 跳过空标签
                            if src.strip() == "":
                                continue
                            self.items.append(Item(src=src, dst=src, tag=path, row=len(self.items)))

        return self.items
