import os
import pickle
import hashlib
import platform

def path_in_different_OS():
    path = os.path.join('home', 'username', 'file.txt')
    print(hashlib.sha256(pickle.dumps(path)).hexdigest())

if __name__ == "__main__":
    print(platform.system())
    path_in_different_OS()
