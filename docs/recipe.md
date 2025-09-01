本项目强烈推荐：基于 [uv](https://docs.astral.sh/uv/) 来管理环境  
> 开发：请额外参考 [在uv中管理pytorch包](https://docs.astral.sh/uv/guides/integration/pytorch/)

# 准备

> 获取源码，并确保下文所有命令的工作目录

```bash
git clone https://github.com/123zdq/KeywordGacha.git

cd KeywordGacha
```



# 方式一：直接用 Python 运行

## 0. 确保 uv 已经 [一键安装](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2)

## 1. 配环境

```bash
# 有Nvidia显卡
uv sync --extra cu129 --no-dev

# 没有Nvidia显卡
uv sync --extra cpu --no-dev
```

## 2. 运行

```bash
uv run src/app.py
```

# 方式二：打包成 exe 再运行

> 不推荐这种方式，因为 Python 其实不太适合打包成 exe

```bash
uv sync --extra cu129 --no-dev
uv pip install pyinstaller
uv run build_support/pyinstaller.py
uv sync --extra cu129 --no-dev
```
打包好的输出在 `dist/` 目录下



# 其它硬件支持

## 仅 cpu

如果你没有Nvidia显卡，建议把本文档中所有的 `uv sync` 命令选项

`--extra cu129` 

全部替换成 

`--extra cpu` 

可以显著降低软件大小

## rocm 与 xpu

暂无



# 其它操作系统

## Linux

没试过，理论上本项目所有代码都是跨平台的，应该可以直接在linux上运行

## MacOS

没用过不了解



# 附录：基础教程

## 关于网络

如果你的网络环境较差，建议用 uv 之前先配置好代理，例如在启动终端后，首先输入下面两行环境变量（根据你的情况填）：

```bash
export HTTP_PROXY="http://192.168.6.6:6666" 
export HTTPS_PROXY="http://192.168.6.6:6666"
```

这两行设置的生效范围与该终端窗口的生命周期一致，此后只要还在这个终端里， uv 或其它软件几乎都会自动用这个代理配置

## 关于 `uv sync` 命令

`uv sync --extra [cu129 | cpu] --no-dev` 

`--extra` 项不能省略

`--no-dev` 表示不安装仅开发时才需要的包，如 ruff，如果想改代码建议不带这项

`sync` 顾名思义，其根据 `pyproject.toml` 的配置来 **自动化地同步** 环境

> **不再需要** ：
查找下载正确的 `Python` 版本并添加环境变量、在项目目录下手动新建 `.venv` 虚拟环境
用 `pip install -r requirements.txt` 命令，运用自身智慧来解决各种依赖冲突的同时反复享受 `pip` 的迟钝速度
用 `pip uninstall` 卸载一些不再需要的包 并留下 大量间接依赖残留 后，不得不删除整个环境，花时间重装以再次享受上述过程

> 例子: 需要打包时就用 `uv pip install` 以 不修改 `pyproject.toml` 的方式往环境安装一些包如 `pyinstaller`，打包完就可以移除掉它和它引入的所有依赖，依然是用 `uv sync --extra cu129 --no-dev` 以将环境精准地还原
