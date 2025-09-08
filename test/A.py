import os
import time
from pathlib import Path


def test_os_path():
    start = time.time()
    for i in range(1000):
        path = os.path.join('folder', 'subfolder', f'file_{i}.txt')
        name = os.path.basename(path)
        dirname = os.path.dirname(path)
        exists = os.path.exists(path)
    return time.time() - start

def test_pathlib():
    start = time.time()
    for i in range(1000):
        path = Path('folder') / 'subfolder' / f'file_{i}.txt'
        name = path.name
        dirname = path.parent
        exists = path.exists()
    return time.time() - start

print(f'os.path time: {test_os_path():.4f} seconds')
print(f'pathlib time: {test_pathlib():.4f} seconds')
