# encoding=utf8
# 基于Doc2vec训练句子向量 https://zhuanlan.zhihu.com/p/36886191
# 不知原因：bert模型在被flask加载之后无法检索使用，但初始化数据时索引和检索正常。
# 参考文章做法，简化bert模型，避免未知坑：https://www.cnblogs.com/yanjj/p/8242595.html
# 使用以上方法没有解决问题！
# 由于存在不可解决的障碍，使用 bert_as_service https://github.com/hanxiao/bert-as-service
# 看来找到上面不可思议异常的原因了，参考代码：https://github.com/hontlong/nlp_xiaojiang/blob/master/FeatureProject/bert/extract_keras_bert_feature.py
# 全局使用，使其可以django、flask、tornado等调用
# graph = None
# global graph
# import tensorflow as tf
# graph = tf.get_default_graph()
# 全局使用，使其可以django、flask、tornado等调用
# with graph.as_default():
#     predicts = model.predict([input_ids, input_type_ids], batch_size=1)

import numpy

__all__ = [
    "BertModel",
]


class BertModel:
    # 这里的bert_client传入的不是连接，而是获取连接的参数，因为连接会随着request线程关闭，不持久
    def __init__(self, bert_client):
        self.bert_client = bert_client

    # db.get_bert_client
    def gen_doc_embedding(self, text):
        print(text)
        vec = self.bert_client().encode([text])
        # 这个向量是没有归一化的
        vec = vec[0]
        vec = vec / numpy.linalg.norm(vec)
        return vec
