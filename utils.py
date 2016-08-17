import random

def str_to_num(s):
    slen = len(s)
    num = 0
    for n, c in enumerate(s):
        mov = slen - (n + 1)
        num += ord(c) << mov
    return num

nid = lambda: ''.join([chr(random.randint(0,255)) for _ in range(20)])

if __name__ == '__main__':
    print repr(nid())
