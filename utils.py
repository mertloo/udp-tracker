
def str_to_num(s):
    slen = len(s)
    num = 0
    for n, c in enumerate(s):
        mov = slen - (n + 1)
        num += ord(c) << mov
    return num

