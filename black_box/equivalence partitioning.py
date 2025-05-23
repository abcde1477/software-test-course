import pickle
import unittest
from datetime import datetime
from decimal import Decimal
from collections import namedtuple, deque
from contextlib import closing
from typing import Any, Optional

# 模块顶层定义
Point = namedtuple("Point", ["x", "y"])

class TestPickleEquivalenceClasses(unittest.TestCase):
    """最终版等价类划分测试"""

    def assertPickleRoundtrip(self, obj: Any, is_valid: bool = True, msg: Optional[str] = None):
        """改进的断言方法"""
        try:
            data = pickle.dumps(obj)
            loaded = pickle.loads(data)
            if is_valid:
                if isinstance(obj, (list, dict)) and hasattr(obj, "__len__"):
                    self.assertEqual(len(obj), len(loaded), "递归结构长度不一致")
                else:
                    self.assertEqual(obj, loaded, msg or f"对象 {type(obj).__name__} 往返序列化失败")
            else:
                self.fail(f"预期不可序列化的对象 {type(obj).__name__} 被成功序列化")
        except (pickle.PicklingError, AttributeError, TypeError) as e:
            if is_valid:
                self.fail(f"有效对象 {type(obj).__name__} 序列化失败: {e}")

    def test_invalid_objects(self):
        """不可序列化对象（无效类）"""
        class NonPicklable:
            def __init__(self):
                self.file = open(__file__, "r")  # 包含不可pickle的属性
            
            def close(self):
                if hasattr(self, "file"):
                    self.file.close()

        # 使用 with 语句确保文件关闭
        with closing(open(__file__, "r")) as file_obj:
            test_cases = [
                NonPicklable(),       # 自定义不可序列化对象
                lambda x: x * 2,      # Lambda函数
                file_obj,            # 文件对象（已在 with 块中管理）
            ]
            
            for case in test_cases:
                with self.subTest(case=case):
                    self.assertPickleRoundtrip(case, is_valid=False)
                
                # 确保非文件对象也被清理
                if hasattr(case, "close") and not isinstance(case, type(file_obj)):
                    case.close()

    # 其他测试方法保持不变...
    def test_recursive_structures(self):
        """递归结构（有效但需特殊处理）"""
        lst = [1, 2, 3]
        lst.append(lst)
        self.assertPickleRoundtrip(lst, is_valid=True)

    def test_valid_containers(self):
        """容器类型（有效类）"""
        test_cases = [[1, 2, 3], {"a": 1}, {1, 2}]
        for case in test_cases:
            with self.subTest(case=case):
                self.assertPickleRoundtrip(case, is_valid=True)

    def test_valid_primitives(self):
        """基本数据类型（有效类）"""
        test_cases = [42, "hello", b"bytes", 3.14, None]
        for case in test_cases:
            with self.subTest(case=case):
                self.assertPickleRoundtrip(case, is_valid=True)

    def test_valid_special_objects(self):
        """特殊对象（有效类）"""
        test_cases = [datetime.now(), Decimal("3.14"), Point(1, 2)]
        for case in test_cases:
            with self.subTest(case=case):
                self.assertPickleRoundtrip(case, is_valid=True)

if __name__ == "__main__":
    unittest.main(verbosity=2)