import sys
from pathlib import Path
import PyInstaller.__main__
from shutil import copytree, rmtree


# 获取 pip 安装的 root 路径（site-packages）
site_packages = Path(sys.prefix) / "Lib" / "site-packages"

# 工作目录 (项目根目录)
pwd = Path(__file__).parent.parent

name = "KeywordGacha"

odir = "dist"

cmd = [
    "src/app.py",
    "--name="+name,
    f"--paths={pwd}",  # 导入项目根目录
    "--clean",  # Clean PyInstaller cache and remove temporary files before building
    # "--icon=./resource/icon.ico",
    "--onedir",  # Create a one-folder bundle containing an executable (default)
    # "--onefile",  # Create a one-file bundled executable
    "--noconfirm",  # Replace output directory (default: SPECPATH/dist/SPECNAME) without asking for confirmation
    f"--distpath=" + odir,  # Where to put the bundled app (default: ./dist)
    
    # 对于 tiktoken pecab pykakasi 这3个库 务必加这几行避免报错：
    "--hidden-import=tiktoken_ext.openai_public",
    "--hidden-import=tiktoken_ext",
    f"--add-data={site_packages/"pecab"}:pecab",
    f"--add-data={site_packages/"pykakasi"}:pykakasi",
]

# 打包前清理输出目录
rmtree(pwd / odir, ignore_errors=True)

# 执行打包
PyInstaller.__main__.run(cmd)

# 复制资源
copytree(pwd / "resource", pwd / odir / name / "resource")
copytree(pwd / "config", pwd / odir / name / "config")

# (可选)清理打包过程中产生的文件
(pwd / "app.spec").unlink(missing_ok=True)
rmtree(pwd / "build", ignore_errors=True)
