import pickle
import sys
import math
import hashlib
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from collections import namedtuple, deque, OrderedDict
from typing import Any, Dict, List, Tuple, Set, FrozenSet, Optional

# 在模块顶层定义所有需要序列化的自定义类
class SimpleClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if not isinstance(other, SimpleClass):
            return False
        return self.x == other.x and self.y == other.y

class MathClass:
    def __init__(self, value):
        self.value = value
    
    def square(self):
        return self.value ** 2
        
    def __eq__(self, other):
        if not isinstance(other, MathClass):
            return False
        return self.value == other.value

class SlotsClass:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if not isinstance(other, SlotsClass):
            return False
        return self.x == other.x and self.y == other.y

# 在模块顶层定义命名元组
Point = namedtuple('Point', ['x', 'y'])

# 自定义测试用例基类，添加哈希比较功能
class PickleTestCase(unittest.TestCase):
    def assertPickleConsistent(self, obj: Any, msg: Optional[str] = None):
        """断言对象序列化后的哈希值一致"""
        try:
            dump1 = pickle.dumps(obj)
            dump2 = pickle.dumps(obj)
            hash1 = hashlib.sha256(dump1).hexdigest()
            hash2 = hashlib.sha256(dump2).hexdigest()
            self.assertEqual(hash1, hash2, msg or f"对象 {type(obj).__name__} 序列化结果不一致")
        except Exception as e:
            self.fail(f"序列化失败: {e}")

    def assertPickleRoundtrip(self, obj: Any, msg: Optional[str] = None):
        """断言对象序列化后反序列化能恢复原始状态"""
        try:
            dump = pickle.dumps(obj)
            loaded = pickle.loads(dump)
            
            # 特殊处理递归对象
            if self._is_recursive(obj):
                self._assert_recursive_equal(obj, loaded, msg)
            else:
                self.assertEqual(obj, loaded, msg or f"对象 {type(obj).__name__} 往返序列化后不一致")
                # 对于复杂对象，额外检查类型一致性
                if hasattr(obj, '__dict__') and hasattr(loaded, '__dict__'):
                    self.assertEqual(obj.__dict__, loaded.__dict__, 
                                 msg or f"对象 {type(obj).__name__} 属性不一致")
                elif hasattr(obj, '__slots__') and hasattr(loaded, '__slots__'):
                    for slot in obj.__slots__:
                        self.assertEqual(getattr(obj, slot), getattr(loaded, slot),
                                     msg or f"对象 {type(obj).__name__} 槽属性不一致")
        except Exception as e:
            self.fail(f"往返序列化失败: {e}")
    
    def _is_recursive(self, obj: Any) -> bool:
        """检测对象是否包含循环引用"""
        memo = set()
        def detect(o):
            if id(o) in memo:
                return True
            memo.add(id(o))
            if isinstance(o, (list, tuple, set, frozenset)):
                return any(detect(item) for item in o)
            if isinstance(o, dict):
                return any(detect(k) or detect(v) for k, v in o.items())
            if hasattr(o, '__dict__'):
                return detect(o.__dict__)
            if hasattr(o, '__slots__'):
                return any(detect(getattr(o, slot)) for slot in o.__slots__)
            return False
        return detect(obj)
    
    def _assert_recursive_equal(self, obj1: Any, obj2: Any, msg: Optional[str] = None):
        """迭代方式比较递归对象，避免递归深度限制"""
        stack = [(obj1, obj2)]
        memo = set()
        
        while stack:
            a, b = stack.pop()
            
            # 跳过已比较对象
            if (id(a), id(b)) in memo:
                continue
            memo.add((id(a), id(b)))
            
            # 类型一致性检查
            self.assertEqual(type(a), type(b), msg or "对象类型不一致")
            
            # 基础类型直接比较
            if isinstance(a, (int, float, str, bytes, bool, type(None))):
                self.assertEqual(a, b, msg or "基础类型值不一致")
                continue
                
            # 列表/元组处理
            if isinstance(a, (list, tuple)):
                self.assertEqual(len(a), len(b), msg or "容器长度不一致")
                # 反向压栈保持原顺序
                stack.extend(zip(reversed(a), reversed(b)))
                continue
                
            # 字典处理
            if isinstance(a, dict):
                self.assertEqual(set(a.keys()), set(b.keys()), msg or "字典键不一致")
                stack.extend((a[k], b[k]) for k in a)
                continue
                
            # 集合处理
            if isinstance(a, (set, frozenset)):
                self.assertEqual(len(a), len(b), msg or "集合大小不一致")
                try:
                    # 尝试按哈希排序
                    a_sorted = sorted(a, key=hash)
                    b_sorted = sorted(b, key=hash)
                except TypeError:
                    # 无法哈希时转为列表
                    a_sorted = list(a)
                    b_sorted = list(b)
                stack.extend(zip(a_sorted, b_sorted))
                continue
                
            # 处理自定义对象的 __dict__
            if hasattr(a, '__dict__') and hasattr(b, '__dict__'):
                stack.append((a.__dict__, b.__dict__))
                continue
                
            # 处理 __slots__ 对象
            if hasattr(a, '__slots__') and hasattr(b, '__slots__'):
                self.assertEqual(set(a.__slots__), set(b.__slots__), msg or "槽属性不一致")
                for slot in a.__slots__:
                    stack.append((getattr(a, slot), getattr(b, slot)))
                continue
                
            # 默认对象比较
            self.assertEqual(a, b, msg or "对象值不一致")

# 测试基础数据类型的边界值
class TestPrimitiveTypes(PickleTestCase):
    def test_integers(self):
        # 最小/最大整数
        self.assertPickleConsistent(sys.maxsize)
        self.assertPickleConsistent(-sys.maxsize - 1)
        # 零和一
        self.assertPickleConsistent(0)
        self.assertPickleConsistent(1)
        # 负整数边界
        self.assertPickleConsistent(-1)
        self.assertPickleConsistent(-9223372036854775808)  # 64位最小整数

    def test_floats(self):
        # 特殊浮点值
        self.assertPickleConsistent(math.inf)
        self.assertPickleConsistent(-math.inf)
        self.assertPickleConsistent(math.nan)
        # 极小/极大值
        self.assertPickleConsistent(sys.float_info.min)
        self.assertPickleConsistent(sys.float_info.max)
        # 高精度值
        self.assertPickleConsistent(1.1234567890123456789)
        # 接近零的值
        self.assertPickleConsistent(1e-308)
        self.assertPickleConsistent(-1e-308)

    def test_strings(self):
        # 空字符串
        self.assertPickleConsistent("")
        # 单字符
        self.assertPickleConsistent("a")
        # 长字符串
        self.assertPickleConsistent("a" * 10000)
        # 特殊字符
        self.assertPickleConsistent("😀")  # emoji
        self.assertPickleConsistent("\0")  # 空字符
        self.assertPickleConsistent("\n\r\t")  # 控制字符
        # 超长字符串
        self.assertPickleConsistent("a" * (2**20))  # 1MB字符串

    def test_bytes(self):
        # 空字节
        self.assertPickleConsistent(b"")
        # 单字节
        self.assertPickleConsistent(b"\x00")
        self.assertPickleConsistent(b"\xff")
        # 特殊字节序列
        self.assertPickleConsistent(b"\x00\x01\x02\x03")
        # 长字节序列
        self.assertPickleConsistent(b"\x01" * 10000)

# 测试容器类型的边界值
class TestContainerTypes(PickleTestCase):
    def test_lists(self):
        # 空列表
        self.assertPickleConsistent([])
        # 单元素列表
        self.assertPickleConsistent([42])
        # 多元素列表
        self.assertPickleConsistent([1, 2, 3, 4, 5])
        # 嵌套列表
        self.assertPickleConsistent([[1, 2], [3, 4], [5, [6, 7]]])
        # 大型列表
        self.assertPickleConsistent(list(range(10000)))
        # 含不同类型的列表
        self.assertPickleConsistent([1, "a", None, [True, False]])

    def test_tuples(self):
        # 空元组
        self.assertPickleConsistent(())
        # 单元素元组
        self.assertPickleConsistent((42,))
        # 多元素元组
        self.assertPickleConsistent((1, 2, 3))
        # 嵌套元组
        self.assertPickleConsistent((1, (2, 3), (4, (5, 6))))
        # 大型元组
        self.assertPickleConsistent(tuple(range(10000)))

    def test_dicts(self):
        # 空字典
        self.assertPickleConsistent({})
        # 单键值对
        self.assertPickleConsistent({"a": 1})
        # 多键值对
        self.assertPickleConsistent({"a": 1, "b": 2, "c": 3})
        # 嵌套字典
        self.assertPickleConsistent({"a": {"b": {"c": 3}}})
        # 大型字典
        self.assertPickleConsistent({str(i): i for i in range(10000)})
        # 含不同类型键值的字典
        self.assertPickleConsistent({1: "a", "b": [2, 3], (4, 5): None})

    def test_sets(self):
        # 空集合
        self.assertPickleConsistent(set())
        # 单元素集合
        self.assertPickleConsistent({42})
        # 多元素集合
        self.assertPickleConsistent({1, 2, 3})
        # 嵌套集合（使用frozenset）
        self.assertPickleConsistent({frozenset({1, 2}), frozenset({3, 4})})
        # 大型集合
        self.assertPickleConsistent(set(range(10000)))

    def test_ordered_dict(self):
        # 有序字典
        od = OrderedDict()
        od["a"] = 1
        od["b"] = 2
        self.assertPickleConsistent(od)

    def test_deque(self):
        # 双端队列
        self.assertPickleConsistent(deque())
        self.assertPickleConsistent(deque([1, 2, 3]))
        self.assertPickleConsistent(deque([1, 2, 3], maxlen=3))

# 测试特殊对象和边界情况
class TestSpecialObjects(PickleTestCase):
    def test_datetime(self):
        # 日期时间对象
        self.assertPickleConsistent(datetime.now())
        self.assertPickleConsistent(datetime(2023, 1, 1, 0, 0, 0))
        self.assertPickleConsistent(timedelta(days=1000))

    def test_decimal(self):
        # 高精度小数
        self.assertPickleConsistent(Decimal('0.1'))
        self.assertPickleConsistent(Decimal('1e+200'))
        self.assertPickleConsistent(Decimal('1e-200'))

    def test_fraction(self):
        # 分数对象
        self.assertPickleConsistent(Fraction(1, 3))
        self.assertPickleConsistent(Fraction(123456789, 987654321))

    def test_namedtuple(self):
        # 使用模块顶层定义的命名元组
        self.assertPickleConsistent(Point(1, 2))
        self.assertPickleRoundtrip(Point(1, 2))

    def test_none(self):
        # None对象
        self.assertPickleConsistent(None)
        self.assertPickleRoundtrip(None)

    def test_boolean(self):
        # 布尔值
        self.assertPickleConsistent(True)
        self.assertPickleConsistent(False)
        self.assertPickleRoundtrip(True)
        self.assertPickleRoundtrip(False)

# 测试递归和循环引用
class TestRecursion(PickleTestCase):
    def test_recursive_list(self):
        # 递归列表
        lst = []
        lst.append(lst)
        self.assertPickleRoundtrip(lst)

    def test_recursive_dict(self):
        # 递归字典
        d = {}
        d['self'] = d
        self.assertPickleRoundtrip(d)

    def test_nested_recursion(self):
        # 嵌套递归结构
        a = [1]
        b = [a]
        a.append(b)
        self.assertPickleRoundtrip(a)

# 测试自定义类
class TestCustomClasses(PickleTestCase):
    def test_simple_class(self):
        obj = SimpleClass(1, 2)
        self.assertPickleRoundtrip(obj)

    def test_class_with_methods(self):
        obj = MathClass(5)
        self.assertPickleRoundtrip(obj)

    def test_class_with_slots(self):
        obj = SlotsClass(1, 2)
        self.assertPickleRoundtrip(obj)

# 测试不同pickle协议
class TestProtocols(PickleTestCase):
    def test_all_protocols(self):
        obj = {'a': [1, 2, 3], 'b': (4, 5), 'c': None}
        
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            try:
                dump1 = pickle.dumps(obj, protocol=protocol)
                dump2 = pickle.dumps(obj, protocol=protocol)
                hash1 = hashlib.sha256(dump1).hexdigest()
                hash2 = hashlib.sha256(dump2).hexdigest()
                self.assertEqual(hash1, hash2, f"协议 {protocol} 下哈希不一致")
                
                loaded = pickle.loads(dump1)
                self.assertEqual(obj, loaded, f"协议 {protocol} 往返序列化失败")
            except (pickle.PicklingError, pickle.UnpicklingError) as e:
                # 某些协议可能不支持特定对象，这是预期的
                print(f"协议 {protocol} 不支持对象: {e}")

# 测试序列化超大对象
class TestLargeObjects(PickleTestCase):
    def test_large_list(self):
        # 100万个元素的列表
        large_list = list(range(1000000))
        self.assertPickleRoundtrip(large_list)

    def test_large_dict(self):
        # 100万个键值对的字典
        large_dict = {str(i): i for i in range(1000000)}
        self.assertPickleRoundtrip(large_dict)

# 测试异常情况
class TestExceptions(PickleTestCase):
    def test_unpicklable_object(self):
        # 测试不可序列化的对象
        with self.assertRaises((pickle.PicklingError, AttributeError)):
            pickle.dumps(lambda x: x * 2)  # 函数不可序列化

        class Unpicklable:
            def __reduce__(self):
                raise pickle.PicklingError("故意不可序列化")
        
        with self.assertRaises(pickle.PicklingError):
            pickle.dumps(Unpicklable())

if __name__ == '__main__':
    unittest.main()