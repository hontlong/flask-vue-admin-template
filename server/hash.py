# python3
# https://www.cnblogs.com/zl1991/p/11820922.html


__all__ = [
    "str_2_id"
]


# BKDRHash
# APHash

# BKDR Hash Function
# input string
# outpu uint32
def bkdr_hash(s):
    seed = 131  # 31 131 1313 13131 131313 etc..
    h = 0
    for c in s:
        h = h * seed + ord(c)
        h = h & 0xffffffff
    return h


# AP Hash Function
# input string
# outpu uint32
def ap_hash(s):
    h = 0
    for i, c in enumerate(s):
        ci = ord(c)
        if i & 1 == 0:
            h ^= (h << 7) ^ ci ^ (h >> 3)
        else:
            h ^= ~((h << 11) ^ ci ^ (h >> 5))
        h = h & 0xffffffff
    return h


# input s
# output uint64
def long_hash(s):
    a = ap_hash(s)
    b = bkdr_hash(s)
    return a << 32 | b


# input s
# output int63 保证正数
def str_2_id(s):
    h = long_hash(s)
    h = h & 0x7fffffffffffffff
    return h


# # test
# # 1亿id的碰撞
# def test_str_2_id():
#     import random
#     import time
#
#     random.seed(time.time_ns())
#     cs = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890_-"
#     n = len(cs)
#
#     def rand_id():
#         s = []
#         while True:
#             c = cs[random.randint(0, n - 1)]
#             s.append(c)
#             if len(s) >= 10:
#                 return "".join(s)
#
#     w = 10000
#     _ids = set()
#     ct = 0
#     for i in range(10000 * w):
#         s = rand_id()
#         _id = str_2_id(s)
#         if _id in _ids:
#             print("冲突:id:%d s:%s" % (_id, s))
#             ct += 1
#         else:
#             _ids.add(_id)
#             # print("正常:id:%d s:%s" % (_id, s))
#         if (i + 1) % w == 0:
#             print("already:", i + 1)
#     print("冲突共:", ct)
#
#
# if __name__ == '__main__':
#     test_str_2_id()
