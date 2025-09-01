非正式文档，开发用的草稿

## 已发现的问题

（疑似）rich 库的console 兼容性：在运行 pyinstaller 打包好的exe时（尚不确定 运行pyinstaller打包好的exe 和本问题的相关性）时，如果程序发生异常，小概率发生（同样的控制变量也无法稳定复现）：终端窗口无法在程序结束后自动关闭，此时终端直接黑屏，点击窗口右上角的 X ，能点得动（按钮会随鼠标单击动作变暗，因此也不会被操作系统报“无响应”）但是点了也不关闭，只能在任务管理器里面手动结束进程，搜索相关issue后推测是 rich 库的console与windows的终端兼容性有问题

纯CPU版本，经过 pyinstaller 打包成 exe 后，推理速度大幅降低，仅为 直接在python中运行源代码 的 三分之一，待尝试：
* 打包cuda版本，但在仅cpu模式运行
* 把 pyinstaller 的 hidden-import 拉满

## 计划中的优化

继续重构代码结构

软件的体积太大，下载安装很麻烦；用pyinstaller打包后性能损失太大（待尝试其它打包工具）

## 计划中的新增

[更精细的批量任务管理](https://github.com/neavo/KeywordGacha/issues/106)

可以跟随原版V0.20.2，增加一个显式的前置替换功能（目前该功能已经隐式地以扫描输入文件夹中的Actor.json进行人名代码替换来实现），但如果没有GUI这个功能不太好加  pre_replacement

继续尝试跟随v0.20.2的特性

可能需要一个简洁的GUI