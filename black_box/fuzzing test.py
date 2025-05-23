import pickle
import hashlib
import random
import string
import datetime
import types
import threading
import csv
from collections import OrderedDict

# 设置种子保证跨平台一致性（使得每次运行结果一致）
random.seed(42)

# 最大嵌套深度、测试次数和输出文件路径
MAX_DEPTH = 3
TEST_COUNT = 20
# 生成随机字符串
def random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 自定义类，用于测试对象的序列化
class CustomClass:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"CustomClass({self.value})"

# 闭包函数生成器（部分对象可能无法被序列化）
def make_closure(x):
    def inner(y):
        return x + y
    return inner

# 随机生成嵌套结构数据，覆盖常见类型与复杂结构
def random_structure(depth=0):
    if depth > MAX_DEPTH:
        return random.choice([None, True, False, random.randint(-1000, 1000), random.random()])

    choice = random.randint(0, 13)
    if choice == 0:
        return random.randint(-1000, 1000)
    elif choice == 1:
        return random.uniform(-1000, 1000)
    elif choice == 2:
        return random_string()
    elif choice == 3:
        return random.choice([True, False])
    elif choice == 4:
        return None
    elif choice == 5:
        return [random_structure(depth + 1) for _ in range(random.randint(0, 4))]
    elif choice == 6:
        return tuple(random_structure(depth + 1) for _ in range(random.randint(0, 4)))
    elif choice == 7:
        return OrderedDict((str(i), random_structure(depth + 1)) for i in range(random.randint(0, 4)))
    elif choice == 8:
        return {random_string(): random_structure(depth + 1) for _ in range(random.randint(0, 4))}
    elif choice == 9:
        s = set()
        for _ in range(random.randint(0, 4)):
            val = random_structure(depth + 1)
            if isinstance(val, (int, str, float)):
                s.add(val)
        return s
    elif choice == 10:
        return CustomClass(random_structure(depth + 1))
    elif choice == 11:
        return datetime.datetime.now()
    elif choice == 12:
        return make_closure(random.randint(0, 10))
    else:
        return None

# 获取对象的类型标签（用于追踪和矩阵输出）
def get_type_label(obj):
    if isinstance(obj, CustomClass):
        return "CustomClass"
    if isinstance(obj, types.FunctionType):
        return "Function"
    if isinstance(obj, datetime.datetime):
        return "datetime"
    if isinstance(obj, set):
        return "set"
    return type(obj).__name__

# 运行测试，序列化与反序列化并检查哈希是否一致，构建可追溯性矩阵
results = []

for i in range(TEST_COUNT):
    result = {
        "Test ID": f"{i:03}",           # 测试编号
        "Type": "",                   # 测试对象类型
        "Hash Match": "",             # 哈希是否匹配
        "Unpickle OK": "",            # 是否成功反序列化
        "Error": ""                    # 错误信息（若有）
    }
    try:
        obj = random_structure()
        result["Type"] = get_type_label(obj)
        serialized1 = pickle.dumps(obj)
        hash1 = hashlib.sha256(serialized1).hexdigest()
        deserialized = pickle.loads(serialized1)
        serialized2 = pickle.dumps(deserialized)
        hash2 = hashlib.sha256(serialized2).hexdigest()
        result["Hash Match"] = hash1 == hash2
        result["Unpickle OK"] = True
    except Exception as e:
        result["Unpickle OK"] = False
        result["Error"] = f"{type(e).__name__} - {e}"
    results.append(result)

    # 打印每次测试结果到控制台
    print(f"Test {i:03}: Type={result['Type']}, HashMatch={result['Hash Match']}, UnpickleOK={result['Unpickle OK']}, Error={result['Error']}")

