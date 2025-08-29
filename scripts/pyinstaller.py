import os
import sys
import PyInstaller.__main__


# 获取 pip 安装的 root 路径（site-packages）
def get_pip_root() -> str:
    return os.path.join(sys.prefix, "lib", "site-packages")


cmd = [
    "src/app.py",
    "--clean",  # Clean PyInstaller cache and remove temporary files before building
    # "--icon=./resource/icon.ico",
    "--onedir",  # Create a one-folder bundle containing an executable (default)
    # "--onefile", # Create a one-file bundled executable
    "--noconfirm",  # Replace output directory (default: SPECPATH/dist/SPECNAME) without asking for confirmation
    "--distpath=dist",  # Where to put the bundled app (default: ./dist)

    # 对于 tiktoken pecab pykakasi 这3个库 务必加这几行避免报错：
    "--hidden-import=tiktoken_ext.openai_public",
    "--hidden-import=tiktoken_ext",
    f"--add-data={get_pip_root()}/pecab:pecab",
    f"--add-data={get_pip_root()}/pykakasi:pykakasi",
]


# 执行打包
PyInstaller.__main__.run(cmd)
