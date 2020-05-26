#!/usr/bin/env python3
# encoding=utf8
import jieba
import pandas
from simhash import Simhash

__all__ = [
    'gen_simhash',
    'compute_simhash_distance'
]


# 输出是simhash的字节数组组成int (64bit的int)
# 输出是 16 位的 16进制 字符串
def gen_simhash(text):
    words = jieba.lcut(text)
    int_v = Simhash(words).value
    return "%016x" % int_v


def compute_simhash_distance(sim1, sim2):
    sim1 = int(sim1, 16)
    sim2 = int(sim2, 16)
    return Simhash(sim1).distance(Simhash(sim2))


def similarity(distance):
    return float(64 - distance) / 64


def main():
    fen = './dataset/text_similar.short.en.tsv'
    fcn = './dataset/text_similar.short.cn.tsv'
    far = './dataset/text_similar.short.ar.tsv'
    jieba.lcut('init')

    data = pandas.read_csv(fcn, sep='\t', header=None)
    # print(data)
    for idx, row in data.iterrows():
        s0 = row[0]
        s1 = row[1]
        flag = row[2]
        sim0 = gen_simhash(s0)
        sim1 = gen_simhash(s1)

        dis = compute_simhash_distance(sim0, sim1)
        sim = similarity(dis)
        print("s0=%s, s1=%s, simhash0=%s, simhash1=%s, sim:%s, flag=%s" % (s0, s1, sim0, sim1, sim, flag))
        # break


if __name__ == '__main__':
    main()
