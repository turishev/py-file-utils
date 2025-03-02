import math

def format_size(size : int):
    s = str(size)
    parts = [s[-3:] if i == 0 else  s[-(i*3 + 3) : -i*3] for i in range(math.ceil(len(s) / 3))]
    return '_'.join(parts)
