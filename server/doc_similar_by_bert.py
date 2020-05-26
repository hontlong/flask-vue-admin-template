# encoding=utf8
# 基于Doc2vec训练句子向量 https://zhuanlan.zhihu.com/p/36886191
import gensim
import jieba
import numpy
import pandas
from numpy.linalg import linalg

TaggededDocument = gensim.models.doc2vec.TaggedDocument

import os

import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer

__all__ = [
    "train",
    "gen_doc_embedding",
    "save_model",
    "load_model"
]

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'  # 必须的否则报错 OMP

# model_path = './data/chinese_L-12_H-768_A-12'
g_model = None
g_tokenizer = None


def is_already_load_model():
    global g_model
    return g_model is not None


# @param: bert_model_file 下载的bert预训练的模型文件
# 如果使用 cased 类型的预训练模型文件 do_lower_case=False
def train(bert_model_path, do_lower_case=False):
    if bert_model_path:
        global g_tokenizer, g_model
        dict_path = '%s/vocab.txt' % bert_model_path
        config_path = '%s/bert_config.json' % bert_model_path
        checkpoint_path = '%s/bert_model.ckpt' % bert_model_path
        g_tokenizer = Tokenizer(dict_path, do_lower_case=do_lower_case)  # 建立分词器
        g_model = build_transformer_model(config_path, checkpoint_path)  # 建立模型，加载权重


def save_model(model_file):
    g_model.save(model_file)


def load_model(model_file, bert_model_path, do_lower_case):
    global g_model, g_tokenizer
    g_model = keras.models.load_model(model_file)
    # print(model.predict([np.array([token_ids]), np.array([segment_ids])]))
    dict_path = '%s/vocab.txt' % bert_model_path
    g_tokenizer = Tokenizer(dict_path, do_lower_case=do_lower_case)  # 建立分词器


# 要求
def gen_doc_embedding(text):
    global g_tokenizer, g_model
    """
    :param text:
    :return: 向量 [float] 注意它不能保证是float32 因为float32在python中是不存在的
        当前实际值是 numpy.array(dtype=float32)
    """
    text = jieba.strdecode(text)
    token_ids, segment_ids = g_tokenizer.encode(text)
    vec = g_model.predict([np.array([token_ids]), np.array([segment_ids])], batch_size=1)
    vec = vec[0][-2]  # 用-2层的隐层作为向量
    vec = vec / linalg.norm(vec)
    return vec


def compute_embedding_similarity(vec1, vec2):
    # v1 = vec1 / linalg.norm(vec1)
    # v2 = vec2 / linalg.norm(vec2)
    # 在生成向量时已经标准化过了
    sim = numpy.dot(vec1, vec2.T)
    sim = 0.5 + 0.5 * sim  # 归一化
    return sim


def main():
    global g_model
    flag = 0

    fen = '../dataset/text_similar.short.en.tsv'
    fcn = '../dataset/text_similar.short.cn.tsv'
    # far = '../dataset/text_similar.short.ar.tsv'
    model_file = '../data/bert_model.bin'
    # bert_model_path = './data/chinese_L-12_H-768_A-12'
    bert_model_path = '../data/multi_cased_L-12_H-768_A-12'

    fin = fcn

    data = pandas.read_csv(fin, sep='\t', header=None)
    # if flag == 0:
    #     train(bert_model_path=bert_model_path, do_lower_case=False)
    #     print("train finish")
    #     save_model(model_file)
    #     print("save model finish")

    # if not g_model:
    load_model(model_file, bert_model_path, do_lower_case=False)
    print("load model finish")

    for idx, row in data.iterrows():
        s0 = row[0]
        s1 = row[1]
        flag = row[2]
        v1 = gen_doc_embedding(s0)
        v2 = gen_doc_embedding(s1)
        print(v1)
        # print(v2)
        sim = compute_embedding_similarity(v1, v2)
        print("s0=%s, s1=%s, sim:%s, flag=%s" % (s0, s1, sim, flag))
        break


if __name__ == '__main__':
    main()
