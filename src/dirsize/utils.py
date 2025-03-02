import math

def format_size(size : int):
    s = str(size)
    if len(s) > 3:
        parts = [s[-3:] if i == 0 else  s[-(i*3 + 3) : -i*3] for i in range(math.ceil(len(s) / 3))]
        parts.reverse()
        return '_'.join(parts)
    else:
        return s
