# 基于Doc2vec训练句子向量 https://zhuanlan.zhihu.com/p/36886191
import multiprocessing
import os
import re

import gensim
import jieba
import numpy
import pandas
from gensim.models.doc2vec import Doc2Vec
from numpy import linalg

TaggededDocument = gensim.models.doc2vec.TaggedDocument

__all__ = [
    'global_config',
    'train',
    'gen_doc_embedding',
    'compute_embedding_similarity',
    "save_model",
    "load_model",
]

stopwords = {" ", ",", ".", "!", "(", ")", "<", ">", "?"}

_zero_vec = numpy.zeros(100)


# 设置
# @param: user_dict_file 用户词典 文件路径 字符串格式 并且词典的字符编码必须是utf8
# @param: stop_word_file
def global_config(user_dict_file=None, stop_word_file=None):
    if user_dict_file:
        jieba.load_userdict(user_dict_file)  # must encoding=utf8
    if stop_word_file:
        tmp = load_stopwords(stop_word_file)  # 读入停用词
        if tmp:
            global stopwords
            stopwords.update(tmp)


# model是预训练的模型
def gen_doc_embedding(model, text):
    """
    :param model:
    :param text:
    :return: 向量 [float] 注意它不能保证是float32 因为float32在python中是不存在的
        当前实际值是 numpy.array(dtype=float32)
    """
    words = [x for x in jieba.lcut(text) if x not in stopwords]
    # print(words)
    # vec = model.infer_vector(doc_words=words, epochs=20)
    # len(vec)=100
    # vec = vec / linalg.norm(vec)
    vect_list = []
    for w in words:
        try:
            vect_list.append(model.wv[w])
        except Exception:
            continue
    # print(vect_list)
    if len(vect_list) <= 0:
        vect_list = [_zero_vec]  # 避免空数据导致计算失败
    vect_list = numpy.array(vect_list)
    vect = vect_list.sum(axis=0)
    vec = vect / numpy.sqrt((vect ** 2).sum())
    vec = vec / linalg.norm(vec)
    return vec


# def similarity(a_vect, b_vect):
#     dot_val = 0.0
#     a_norm = 0.0
#     b_norm = 0.0
#     for a, b in zip(a_vect, b_vect):
#         dot_val += a * b
#         a_norm += a ** 2
#         b_norm += b ** 2
#     if a_norm == 0.0 or b_norm == 0.0:
#         cos = -1
#     else:
#         cos = dot_val / ((a_norm * b_norm) ** 0.5)
#
#     return cos


def compute_embedding_similarity(vec1, vec2):
    # v1 = vec1 / linalg.norm(vec1)
    # v2 = vec2 / linalg.norm(vec2)
    # 在生成向量时已经标准化过了
    sim = numpy.dot(vec1, vec2.T)
    return sim


def load_stopwords(fin):
    ws = []
    with open(fin, 'r') as f:
        for line in f:
            w = line.strip('\n')
            # 转为unicode，这个是jieba的输出标准str(unicode)
            w = jieba.strdecode(w)
            ws.append(w)
    w = '\n'
    w = jieba.strdecode(w)
    ws.append(w)
    return set(ws)


# docs = [content text]
def read_dataset(data):
    texts = []
    for idx, row in data.iterrows():
        s0 = row[0]
        s1 = row[1]
        texts.append(s0)
        texts.append(s1)
    return texts


def _text_to_words(text):
    ws = []
    ss = re.split(r'\s+', text)
    for s in ss:
        # print(s)
        s = jieba.strdecode(s)  # 统一的转为unicode编码
        if _is_chinese_chars(s):
            words = jieba.lcut(s)
            ws.extend(words)
        else:
            ws.append(s)
    ws = list(filter(lambda w: w not in stopwords, ws))
    ws = [w for w in ws if w not in stopwords]
    return ws


def _is_chinese_chars(text):
    for char in text:
        cp = ord(char)
        if _is_chinese_char(cp):
            return True
    return False


def _is_chinese_char(cp):
    """Checks whether CP is the codepoint of a CJK character."""
    # This defines a "chinese character" as anything in the CJK Unicode block:
    #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
    #
    # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
    # despite its name. The modern Korean Hangul alphabet is a different block,
    # as is Japanese Hiragana and Katakana. Those alphabets are used to write
    # space-separated words, so they are not treated specially and handled
    # like the all of the other languages.
    if ((0x4E00 <= cp <= 0x9FFF) or  #
            (0x3400 <= cp <= 0x4DBF) or  #
            (0x20000 <= cp <= 0x2A6DF) or  #
            (0x2A700 <= cp <= 0x2B73F) or  #
            (0x2B740 <= cp <= 0x2B81F) or  #
            (0x2B820 <= cp <= 0x2CEAF) or
            (0xF900 <= cp <= 0xFAFF) or  #
            (0x2F800 <= cp <= 0x2FA1F)):  #
        return True

    return False


# doc = text content
# docs = [doc]
# @param texts [text] text是一段文字
def train(texts, vector_size=100, epochs=20):
    docs = []
    for idx, text in enumerate(texts):
        words = _text_to_words(text)
        if len(words) <= 0:
            continue
        # print(words)
        doc = TaggededDocument(words=words, tags=[idx])
        docs.append(doc)

    # D2V参数解释：
    # min_count：忽略所有单词中单词频率小于这个值的单词。
    # window：窗口的尺寸。（句子中当前和预测单词之间的最大距离）
    # size:特征向量的维度
    # sample：高频词汇的随机降采样的配置阈值，默认为1e-3，范围是(0,1e-5)。
    # negative: 如果>0,则会采用negativesampling，用于设置多少个noise words（一般是5-20）。默认值是5。
    # workers：用于控制训练的并行数。
    # dm=0 : 使用Doc2vec的DBOW算法，类似于skip-gram，如果dm=1 使用DM算法。默认值 dm=1
    # hs=0 : 使用负采样 negative sampling will be used
    # hs=1 : 使用 hierarchical softmax 优化模型
    # model_dm = Doc2Vec(docs, dm=1, min_count=10, window=3, vector_size=vector_size, sample=1e-3, hs=1, negative=5,
    cores = multiprocessing.cpu_count()
    # model_dm = Doc2Vec(dm=0, hs=0, min_count=3, window=5, sample=0, negative=5, vector_size=vector_size, workers=cores)
    model_dbow = Doc2Vec(docs, dm=0, hs=0, min_count=0, window=5, sample=1e-5, negative=5, vector_size=vector_size,
                         workers=cores)
    # sample 的值影响较大 1e-3 ==> 0.97 1e-5 ==> 0.49，这个参数越低，高频词，就以更低的采样比采样，

    model = model_dbow
    # model.build_vocab(docs, progress_per=10)
    # model.build_vocab(docs, update=True) #可以持续更新模型库
    model.train(docs, total_examples=model.corpus_count, epochs=epochs)
    return model


def save_model(model, model_file):
    model.save(model_file)


def load_model(model_file):
    model = Doc2Vec.load(model_file)
    return model


def query(model_dm, doc):
    # doc = doc or '申请贷款需要什么条件？'
    words = [x for x in jieba.lcut(doc) if x not in stopwords]
    # print(json.dumps(words, encoding="UTF-8", ensure_ascii=False))
    inferred_vector_dm = model_dm.infer_vector(doc_words=words, epochs=1)
    print(len(inferred_vector_dm))
    # 返回相似的句子
    sims = model_dm.docvecs.most_similar([inferred_vector_dm], topn=10)
    return sims[0]


def main():
    # flag = 1

    fen = '../dataset/text_similar.short.en.tsv'
    fcn = '../dataset/text_similar.short.cn.tsv'
    far = '../dataset/text_similar.short.ar.tsv'
    full = '../data/lcqmc-NLP数据资源/lcqmc_train.tsv'
    model_file = '../data/doc2vec_model.bin'

    global_config(stop_word_file="../data/stopwords.txt")

    fin = full

    data = pandas.read_csv(fin, sep='\t', header=None)

    if os.path.exists(model_file):
        model = load_model(model_file)
        print("load model finish")
    else:
        texts = read_dataset(data)
        print("get dataset finish")
        model = train(texts)
        print("train finish")
        save_model(model, model_file)
        print("save model finish")

    for idx, row in data.iterrows():
        s0 = row[0]
        s1 = row[1]
        # s0 = "谁有狂三这张高清的"
        # s1 = "谁有狂三这张高清的"
        # s1 = "这张高清图，谁有"
        # s1 = "完全不嫌疼痛都是其他字符"
        flag = row[2]
        v1 = gen_doc_embedding(model, s0)
        v2 = gen_doc_embedding(model, s1)
        sim = compute_embedding_similarity(v1, v2)
        print("s0=%s, s1=%s, sim:%s, flag=%s" % (s0, s1, sim, flag))
        break


if __name__ == '__main__':
    main()
