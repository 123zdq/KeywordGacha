import threading
from dataclasses import dataclass, field


@dataclass
class TestField:
    lock: threading.Lock = field(init=False, repr=False, compare=False, default_factory=threading.Lock)
    value: int = 0

@dataclass
class TestPostInit:
    lock: threading.Lock = field(init=False, repr=False, compare=False)
    value: int = 0

    def __post_init__(self):
        self.lock = threading.Lock()

# 测试 1: 构造函数参数
try:
    t1 = TestField(lock=threading.Lock())  # 应该失败
except TypeError as e:
    print(f"Field方式构造函数参数测试: {e}")

try:
    t2 = TestPostInit(lock=threading.Lock())  # 应该失败
except TypeError as e:
    print(f"PostInit方式构造函数参数测试: {e}")

# 测试 2: repr 输出
t3 = TestField(value=1)
t4 = TestPostInit(value=1)
print(f"Field方式repr: {repr(t3)}")
print(f"PostInit方式repr: {repr(t4)}")

# 测试 3: 比较操作
t5 = TestField(value=1)
t6 = TestField(value=1)
t7 = TestPostInit(value=1)
t8 = TestPostInit(value=1)
print(f"Field方式比较: {t5 == t6}")
print(f"PostInit方式比较: {t7 == t8}")

# 测试 4: 独立Lock
t9 = TestField()
t10 = TestField()
t11 = TestPostInit()
t12 = TestPostInit()
print(f"Field方式Lock独立: {t9.lock is not t10.lock}")
print(f"PostInit方式Lock独立: {t11.lock is not t12.lock}")
