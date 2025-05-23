import pickle
import hashlib
import platform

def show_protocol_message():
    print("default protocol test")
    print("default pickle protocol:",pickle.DEFAULT_PROTOCOL)

def protocol_in_different_version():
    show_protocol_message()
    data_str = "ABCD"
    print("SHA-256:", hashlib.sha256(pickle.dumps(data_str)).hexdigest())

def dict_in_different_version():
    print("dict test:")
    data_dict = {"z":0,"a":1,"b":2,"c":3}
    serialized = pickle.dumps(data_dict, protocol=4)
    sha256_hash = hashlib.sha256(serialized).hexdigest()
    print("SHA-256:", sha256_hash)

if __name__ =="__main__":
    print("Python version:", platform.python_version())
    print("---------")
    dict_in_different_version()
    print("---------")
    protocol_in_different_version()
    