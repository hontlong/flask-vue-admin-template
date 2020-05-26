# encoding=utf8
# 基于Doc2vec训练句子向量 https://zhuanlan.zhihu.com/p/36886191
import jieba
import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model


def ___():
    build_transformer_model()


from bert4keras.tokenizers import Tokenizer
from numpy.linalg import linalg

__all__ = [
]

g_model = None
g_tokenizer = None


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


def main():
    model_file = '../data/bert_model.bin'
    bert_model_path = '../data/multi_cased_L-12_H-768_A-12'

    load_model(model_file, bert_model_path, do_lower_case=False)
    print("load model finish")

    text = "谁的高清图"
    vec = gen_doc_embedding(text)
    print(vec)


if __name__ == '__main__':
    main()
