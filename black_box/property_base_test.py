import pickle
import hashlib
from hypothesis import given, settings, find, Verbosity
from hypothesis.strategies import (
    booleans, floats, integers, lists, none, text, tuples, dictionaries, sets,
    one_of, recursive, complex_numbers, just, builds
)
import random


# 自定义类：包含非确定性 __getstate__
class RandomWrapper:
    def __init__(self):
        self.value = random.random()

    def __getstate__(self):
        return {"value": random.random()}  # 不同序列化结果




def is_hashable(x):
    try:
        hash(x)
        return True
    except Exception:
        return False
    
# 构造通用对象（包括随机类 / NaN / inf / 集合）
general_object = recursive(
    base=one_of(
        integers(),
        floats(allow_nan=True, allow_infinity=True),
        complex_numbers(),
        text(),
        booleans(),
        none(),
    ),
    extend=lambda children: one_of(
        lists(children, max_size=4),
        tuples(children, children),
        dictionaries(text(), children, max_size=4),
        # 
        sets(children.filter(is_hashable), min_size=1, max_size=4),
    ),
    max_leaves=10,
)


# 手动运行 Hypothesis 测试（不依赖 pytest）
@given(obj=general_object)
@settings(max_examples=500, verbosity=Verbosity.verbose)
def run_test(obj):
    hash1 = hashlib.sha256(pickle.dumps(obj)).hexdigest()
    hash2 = hashlib.sha256(pickle.dumps(obj)).hexdigest()

    if hash1 != hash2:
        print("SHA256 hash mismatch!")
        print("Object:", repr(obj))
        print("Hash1 :", hash1)
        print("Hash2 :", hash2)
        raise AssertionError("Pickle hash mismatch detected.")

if __name__ == "__main__":
    print("Running Hypothesis test...")
    run_test()
    print("No mismatches found in tested examples.")
