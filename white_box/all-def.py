import io
import pickle1
import unittest
import types
from struct import pack, unpack
from unittest.mock import Mock, patch, MagicMock
from pickle1 import _Framer, _Unframer, _getattribute, whichmodule, encode_long, decode_long, _NoValue, _Pickler, _Unpickler, PicklingError, UnpicklingError, HIGHEST_PROTOCOL

class TestClass:
    def __init__(self, value):
        self.value = value
    def __eq__(self, other):
        return isinstance(other, TestClass) and self.value == other.value

class TestPickleModuleLevel(unittest.TestCase):
    """Variable definitions at the test module level"""
    
    def test_module_variables(self):
        # Test module-level variables in the pickle1 module
        self.assertEqual(pickle1.format_version, "4.0")
        self.assertEqual(pickle1.HIGHEST_PROTOCOL, 5)
        self.assertEqual(pickle1.DEFAULT_PROTOCOL, 4)
        self.assertIsInstance(pickle1.__all__, list)
        self.assertIn("Pickler", pickle1.__all__)
        self.assertIn("Unpickler", pickle1.__all__)
        self.assertIn("dump", pickle1.__all__)
        self.assertIn("dumps", pickle1.__all__)
        self.assertIn("load", pickle1.__all__)
        self.assertIn("loads", pickle1.__all__)

class TestPickleOpcodes(unittest.TestCase):
    """Test Pickle opcode definition"""
    
    def test_basic_opcodes(self):
        # Test basic opcodes in the pickle1 module
        self.assertEqual(pickle1.MARK, b'(')
        self.assertEqual(pickle1.STOP, b'.')
        self.assertEqual(pickle1.POP, b'0')
        self.assertEqual(pickle1.POP_MARK, b'1')
        self.assertEqual(pickle1.DUP, b'2')
        self.assertEqual(pickle1.FLOAT, b'F')
        self.assertEqual(pickle1.INT, b'I')
        self.assertEqual(pickle1.BININT, b'J')
        self.assertEqual(pickle1.BININT1, b'K')
        self.assertEqual(pickle1.LONG, b'L')
        self.assertEqual(pickle1.BININT2, b'M')
        self.assertEqual(pickle1.NONE, b'N')
        self.assertEqual(pickle1.PERSID, b'P')
        self.assertEqual(pickle1.BINPERSID, b'Q')
        self.assertEqual(pickle1.REDUCE, b'R')
        self.assertEqual(pickle1.STRING, b'S')
        self.assertEqual(pickle1.BINSTRING, b'T')
        self.assertEqual(pickle1.SHORT_BINSTRING, b'U')
        self.assertEqual(pickle1.UNICODE, b'V')
        self.assertEqual(pickle1.BINUNICODE, b'X')
        self.assertEqual(pickle1.APPEND, b'a')
        self.assertEqual(pickle1.BUILD, b'b')
        self.assertEqual(pickle1.GLOBAL, b'c')
        self.assertEqual(pickle1.DICT, b'd')
        self.assertEqual(pickle1.EMPTY_DICT, b'}')
        self.assertEqual(pickle1.APPENDS, b'e')
        self.assertEqual(pickle1.GET, b'g')
        self.assertEqual(pickle1.BINGET, b'h')
        self.assertEqual(pickle1.INST, b'i')
        self.assertEqual(pickle1.LONG_BINGET, b'j')
        self.assertEqual(pickle1.LIST, b'l')
        self.assertEqual(pickle1.EMPTY_LIST, b']')
        self.assertEqual(pickle1.OBJ, b'o')
        self.assertEqual(pickle1.PUT, b'p')
        self.assertEqual(pickle1.BINPUT, b'q')
        self.assertEqual(pickle1.LONG_BINPUT, b'r')
        self.assertEqual(pickle1.SETITEM, b's')
        self.assertEqual(pickle1.TUPLE, b't')
        self.assertEqual(pickle1.EMPTY_TUPLE, b')')
        self.assertEqual(pickle1.SETITEMS, b'u')
        self.assertEqual(pickle1.BINFLOAT, b'G')
        self.assertEqual(pickle1.TRUE, b'I01\n')
        self.assertEqual(pickle1.FALSE, b'I00\n')

class TestExceptionClasses(unittest.TestCase):
    """Test exception class definition"""
    
    def test_pickle_error(self):
        # Test raising PickleError exception
        with self.assertRaises(pickle1.PickleError):
            raise pickle1.PickleError("test error")
    
    def test_pickling_error(self):
        # Test raising PicklingError exception and its inheritance
        with self.assertRaises(pickle1.PicklingError):
            raise pickle1.PicklingError("test pickling error")
        self.assertTrue(issubclass(pickle1.PicklingError, pickle1.PickleError))
    
    def test_unpickling_error(self):
        # Test raising UnpicklingError exception and its inheritance
        with self.assertRaises(pickle1.UnpicklingError):
            raise pickle1.UnpicklingError("test unpickling error")
        self.assertTrue(issubclass(pickle1.UnpicklingError, pickle1.PickleError))
    
    def test_stop_exception(self):
        # Test raising _Stop exception and its value
        try:
            raise pickle1._Stop("test value")
        except pickle1._Stop as e:
            self.assertEqual(e.value, "test value")

class TestFramer(unittest.TestCase):
    """Test Class _Framer"""
    
    def test_init_definition(self):
        # Test the initialization of _Framer class
        mock_write = Mock()
        framer = _Framer(mock_write)
        self.assertEqual(framer.file_write, mock_write)  
        self.assertIsNone(framer.current_frame)         
    
    def test_start_framing_definition(self):
        # Test the start_framing method of _Framer class
        framer = _Framer(Mock())
        framer.start_framing()
        self.assertIsInstance(framer.current_frame, io.BytesIO)  
    
    def test_write_definitions(self):
        # Test the write method of _Framer class
        framer = _Framer(Mock())
        framer.start_framing()
        bytes_written = framer.write(b'test')
        self.assertEqual(bytes_written, 4)  
        
        framer.current_frame = None
        framer.write(b'direct')
    
    def test_commit_frame_definitions(self):
        # Test the commit_frame method of _Framer class
        framer = _Framer(Mock())
        framer.start_framing()
        framer.write(b'data')
        
        framer.commit_frame(force=True)
        self.assertIsInstance(framer.current_frame, io.BytesIO)

class TestUnframer(unittest.TestCase):
    
    def test_init_definition(self):
        # Test the initialization of _Unframer class
        unframer = _Unframer(Mock(), Mock())
        self.assertIsNone(unframer.current_frame)  
    
    def test_readinto_definitions(self):
        # Test the readinto method of _Unframer class
        unframer = _Unframer(lambda n: b'fallback', None)
        unframer.current_frame = io.BytesIO(b'123')
        buf = bytearray(2)
        n = unframer.readinto(buf)
        self.assertEqual(n, 2)  
        
        unframer.current_frame = io.BytesIO(b'')
        unframer.readinto(bytearray(1))
        self.assertIsNone(unframer.current_frame)  
    
    def test_load_frame_definition(self):
        # Test the load_frame method of _Unframer class
        unframer = _Unframer(lambda n: b'frame', None)
        unframer.load_frame(5)
        self.assertEqual(unframer.current_frame.getvalue(), b'frame')  

class TestPickleToolsAllDef(unittest.TestCase):
    """Strict full definition test (only covers variable definition points)"""

    def test_getattribute_definitions(self):
        """Test the variable definitions of _getattribute"""
        class TestObj:
            attr = "value"
            nested = type('Nested', (), {'deep': 42})()
        
        # Definition point 1: Initial assignment of top
        obj, parent = _getattribute(TestObj(), 'attr')
        self.assertEqual(obj, "value")
        
        # Definition point 2: Assignment of parent in nested attributes
        obj, parent = _getattribute(TestObj(), 'nested.deep')
        self.assertEqual(obj, 42)
        self.assertTrue(hasattr(parent, 'deep'))

    def test_whichmodule_definitions(self):
        """Test the variable definitions of whichmodule"""
        # Definition point 1: module_name is obtained from __module__
        class TestClass:
            __module__ = 'test.module'
        self.assertEqual(whichmodule(TestClass, 'any'), 'test.module')
        
        # Definition point 2: Test standard library modules
        import io
        self.assertEqual(whichmodule(io.BytesIO, '__name__'), '_io')
        
        # Definition point 3: Test dynamic modules (optional)
        test_module = types.ModuleType('valid.module')
        test_obj = object()
        test_module.some_attr = test_obj
        with patch.dict('sys.modules', {'valid.module': test_module}):
            self.assertEqual(whichmodule(test_obj, 'some_attr'), 'valid.module')

    def test_encode_long_definitions(self):
        """Test the variable definitions of encode_long"""
        # Definition point 1: Calculation of nbytes
        self.assertEqual(encode_long(255), b'\xff\x00')
        
        # Definition point 2: Truncation of result (negative value optimization)
        self.assertEqual(encode_long(-32768), b'\x00\x80')
        
        # Definition point 3: Special case for zero value
        self.assertEqual(encode_long(0), b'')

    def test_decode_long_definitions(self):
        """Test the variable definitions of decode_long"""
        # Definition point: Definition of return value
        self.assertEqual(decode_long(b'\xff\x00'), 255)
        self.assertEqual(decode_long(b''), 0)

    def test_no_value_definition(self):
        """Test the definition of _NoValue"""
        # Definition point: Existence of singleton object
        self.assertIsInstance(_NoValue, object)

class TestPickler(unittest.TestCase):
    
    def setUp(self):
        self.buffer = io.BytesIO()
    
    def test_basic_types(self):
        """Test pickling of basic Python types"""
        test_data = [
            None,
            True,
            False,
            42,
            3.14159,
            "hello world",
            b"binary data",
            [1, 2, 3],
            {'a': 1, 'b': 2},
            {1, 2, 3},
            (1, 2, 3)
        ]
        
        for obj in test_data:
            self.buffer.seek(0)
            self.buffer.truncate()
            pickler = _Pickler(self.buffer)
            pickler.dump(obj)
            
            self.buffer.seek(0)
            unpickler = _Unpickler(self.buffer)
            result = unpickler.load()
            
            self.assertEqual(obj, result)
    
    def test_protocol_versions(self):
        """Test different protocol versions"""
        obj = {'key': 'value', 'nums': [1, 2, 3]}
        
        for proto in range(0, HIGHEST_PROTOCOL + 1):
            self.buffer.seek(0)
            self.buffer.truncate()
            pickler = _Pickler(self.buffer, protocol=proto)
            pickler.dump(obj)
            
            self.buffer.seek(0)
            unpickler = _Unpickler(self.buffer)
            result = unpickler.load()
            
            self.assertEqual(obj, result)
    
    def test_recursive_objects(self):
        """Test pickling of recursive objects"""
        # Recursive list
        a = []
        a.append(a)
        
        self.buffer.seek(0)
        self.buffer.truncate()
        pickler = _Pickler(self.buffer)
        pickler.dump(a)
        
        self.buffer.seek(0)
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        
        self.assertIs(result[0], result)
    
    def test_memoization(self):
        """Test that objects are properly memoized"""
        shared = [1, 2, 3]
        obj = [shared, shared]
        
        self.buffer.seek(0)
        self.buffer.truncate()
        pickler = _Pickler(self.buffer)
        pickler.dump(obj)
        
        self.buffer.seek(0)
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        
        self.assertIs(result[0], result[1])
    
    def test_unpicklable_objects(self):
        """Test handling of unpicklable objects"""
        # Lambda functions can't be pickled
        obj = lambda x: x + 1
        
        pickler = _Pickler(self.buffer)
        with self.assertRaises(PicklingError):
            pickler.dump(obj)
    
    def test_large_objects(self):
        """Test pickling of large objects"""
        large_list = list(range(10000))
        large_bytes = b'x' * (10 * 1024 * 1024)  # 10MB
        
        self.buffer.seek(0)
        self.buffer.truncate()
        pickler = _Pickler(self.buffer, protocol=4)
        pickler.dump(large_list)
        pickler.dump(large_bytes)
        
        self.buffer.seek(0)
        unpickler = _Unpickler(self.buffer)
        result_list = unpickler.load()
        result_bytes = unpickler.load()
        
        self.assertEqual(large_list, result_list)
        self.assertEqual(large_bytes, result_bytes)
    
    def test_clear_memo(self):
        """Test clear_memo method"""
        obj1 = [1, 2, 3]
        obj2 = {'a': 1, 'b': 2}
        
        pickler = _Pickler(self.buffer)
        pickler.dump(obj1)
        self.assertIn(id(obj1), pickler.memo)
        
        pickler.clear_memo()
        self.assertEqual(len(pickler.memo), 0)
        
        pickler.dump(obj2)
        self.assertIn(id(obj2), pickler.memo)
    
    def test_custom_reduce(self):
        """Test objects with __reduce__ method"""
        class CustomReduce:
            def __reduce__(self):
                return (list, ([1, 2, 3],))
        
        obj = CustomReduce()
        
        pickler = _Pickler(self.buffer)
        pickler.dump(obj)
        
        self.buffer.seek(0)
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        
        self.assertEqual(result, [1, 2, 3])
    
    def test_protocol_errors(self):
        """Test invalid protocol values"""
        with self.assertRaises(ValueError):
            _Pickler(self.buffer, protocol=7)
        
        with self.assertRaises(ValueError):
            _Pickler(self.buffer, protocol = HIGHEST_PROTOCOL + 1)
    
    def test_buffer_callback(self):
        """Test buffer_callback functionality (protocol 5+)"""
        # Ensure _Pickler has PickleBuffer attribute and protocol version is 5
        if hasattr(_Pickler, 'PickleBuffer') and HIGHEST_PROTOCOL >= 5:
            buffers = []

            def callback(buf):
                buffers.append(buf)
                return False  # Mark as out-of-band

            data = b'large binary data' * 1000
            pickler = _Pickler(self.buffer, protocol=5, buffer_callback=callback)
            pickler.dump(data)

            self.assertEqual(len(buffers), 1)
            self.assertEqual(bytes(buffers[0]), data)
        else:
            self.skipTest("PickleBuffer not available or protocol < 5")

class TestUnpickler(unittest.TestCase):
    
    def setUp(self):
        self.buffer = io.BytesIO()
    
    def pickle_data(self, obj, protocol=None):
        """Helper method to pickle data to the buffer"""
        self.buffer.seek(0)
        self.buffer.truncate()
        pickler = _Pickler(self.buffer, protocol=protocol)
        pickler.dump(obj)
        self.buffer.seek(0)
    
    def test_basic_types(self):
        """Test unpickling of basic Python types"""
        test_data = [
            None,
            True,
            False,
            42,
            3.14159,
            "hello world",
            b"binary data",
            [1, 2, 3],
            {'a': 1, 'b': 2},
            {1, 2, 3},
            (1, 2, 3)
        ]
        
        for obj in test_data:
            self.pickle_data(obj)
            unpickler = _Unpickler(self.buffer)
            result = unpickler.load()
            self.assertEqual(obj, result)
    
    def test_protocol_versions(self):
        """Test different protocol versions"""
        obj = {'key': 'value', 'nums': [1, 2, 3]}
        
        for proto in range(0, HIGHEST_PROTOCOL + 1):
            self.pickle_data(obj, protocol=proto)
            unpickler = _Unpickler(self.buffer)
            result = unpickler.load()
            self.assertEqual(obj, result)
    
    def test_recursive_objects(self):
        """Test unpickling of recursive objects"""
        # Create and pickle a recursive list
        a = []
        a.append(a)
        self.pickle_data(a)
        
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        
        self.assertIs(result[0], result)
    
    def test_memo_handling(self):
        """Test that memo is properly handled"""
        shared = [1, 2, 3]
        obj = [shared, shared]
        self.pickle_data(obj)
        
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        
        self.assertIs(result[0], result[1])
    
    def test_corrupted_data(self):
        """Test handling of corrupted pickle data"""
        # First pickle valid data
        self.pickle_data([1, 2, 3])
        
        # Corrupt the pickle data by truncating it
        corrupted_data = self.buffer.getvalue()[:-2]
        self.buffer = io.BytesIO(corrupted_data)
        
        unpickler = _Unpickler(self.buffer)
        with self.assertRaises(EOFError):
            unpickler.load()
    
    def test_large_objects(self):
        """Test unpickling of large objects"""
        large_list = list(range(1000))
        large_bytes = b'x' * ( 1024 * 1024)  # 1MB
        
        self.pickle_data(large_list)
        unpickler = _Unpickler(self.buffer)
        result_list = unpickler.load()
        self.assertEqual(large_list, result_list)
        
        self.pickle_data(large_bytes)
        unpickler = _Unpickler(self.buffer)
        result_bytes = unpickler.load()
        self.assertEqual(large_bytes, result_bytes)
    
    def test_custom_classes(self):
        """Test unpickling of custom class instances"""
        obj = TestClass(42)
        self.pickle_data(obj)
        
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        
        self.assertEqual(obj.value, result.value)
        self.assertIsInstance(result, TestClass)
    
    def test_persistent_load(self):
        """Test persistent_load functionality"""
        pid = "some_persistent_id"
        
        # Create a pickle with a persistent ID
        self.buffer.seek(0)
        self.buffer.truncate()
        pickler = _Pickler(self.buffer)
        pickler.save_pers(pid)
        pickler.write(b'.')  # STOP opcode
        self.buffer.seek(0)
        
        # Test with default persistent_load
        unpickler = _Unpickler(self.buffer)
        with self.assertRaises(UnpicklingError):
            unpickler.load()
        
        # Test with custom persistent_load
        class CustomUnpickler(_Unpickler):
            def persistent_load(self, pid):
                return f"loaded_{pid}"
        
        self.buffer.seek(0)
        unpickler = CustomUnpickler(self.buffer)
        result = unpickler.load()
        self.assertEqual(result, f"loaded_{pid}")
    
    def test_find_class(self):
        """Test find_class functionality"""
        # Create a pickle with a global reference to a safe builtin
        self.pickle_data(sum)
        
        # Test with default find_class
        unpickler = _Unpickler(self.buffer)
        result = unpickler.load()
        self.assertIs(result, sum)
        
        # Test with restricted find_class
        class RestrictedUnpickler(_Unpickler):
            allowed_globals = {'builtins.sum': sum}
            
            def find_class(self, module, name):
                key = f"{module}.{name}"
                if key in self.allowed_globals:
                    return self.allowed_globals[key]
                raise UnpicklingError(f"global '{module}.{name}' is forbidden")
        
        self.buffer.seek(0)
        unpickler = RestrictedUnpickler(self.buffer)
        result = unpickler.load()
        self.assertIs(result, sum)
        
        # Test with forbidden class
        self.pickle_data(eval)
        self.buffer.seek(0)
        unpickler = RestrictedUnpickler(self.buffer)
        with self.assertRaises(UnpicklingError):
            unpickler.load()
    
    def test_buffer_handling(self):
        """Test buffer handling (protocol 5+)"""
        if not hasattr(pickle1, 'PickleBuffer') or HIGHEST_PROTOCOL < 5:
            self.skipTest("PickleBuffer not available or protocol < 5")
        
        buf = b'test_buffer'
        buffers = [buf]
        
        # Use standard pickle to create data containing buffer references
        self.buffer = io.BytesIO()
        pickler = pickle1.Pickler(self.buffer, protocol=5)
        pickler.dump(buf)
        self.buffer.seek(0)
        
        # Test 1: Providing buffers parameter should unpickle correctly
        unpickler = _Unpickler(self.buffer, buffers=buffers)
        result = unpickler.load()
        self.assertEqual(result, buf)
        
        # Test 2: Not providing buffers parameter should raise an exception
        self.buffer.seek(0)
        unpickler = _Unpickler(self.buffer)  # Not providing buffers
        with self.assertRaises(UnpicklingError):
            unpickler.load()
    
    def test_fix_imports(self):
        """Test fix_imports parameter"""
        # Create a simple list object and pickle it using Python 2 style module names
        original_list = []
        self.buffer = io.BytesIO()
        pickler = pickle1.Pickler(self.buffer, protocol=2)
        pickler.dump(original_list)
        pickle_data = self.buffer.getvalue()
        
        # Replace 'builtins' with Python 2's '__builtin__'
        py2_pickle = pickle_data.replace(b'builtins', b'__builtin__')
        self.buffer = io.BytesIO(py2_pickle)
        
        # Test fix_imports=True should automatically convert
        unpickler = _Unpickler(self.buffer, fix_imports=True)
        result = unpickler.load()
        self.assertEqual(result, original_list)
        
        # Test fix_imports=False should reject Python 2 style import names
        self.buffer.seek(0)
        unpickler = _Unpickler(self.buffer, fix_imports=False)
        with self.assertRaises((UnpicklingError, AttributeError, ImportError)):
            unpickler.load()

class TestDumpLoadFunctions(unittest.TestCase):
    """Test dump/load series functions"""
    
    def test_dump_load(self):
        f = io.BytesIO()
        pickle1._dump([1, 2, 3], f)
        f.seek(0)
        self.assertEqual(pickle1._load(f), [1, 2, 3])
    
    def test_dumps_loads(self):
        data = pickle1._dumps({"a": 1, "b": 2})
        self.assertIsInstance(data, bytes)
        self.assertEqual(pickle1._loads(data), {"a": 1, "b": 2})
    
    def test_protocol_handling(self):
        # Test different protocol versions
        for proto in range(0, pickle1.HIGHEST_PROTOCOL + 1):
            data = pickle1._dumps([1, 2, 3], protocol=proto)
            self.assertEqual(pickle1._loads(data), [1, 2, 3])

if __name__ == "__main__":
    unittest.main()
