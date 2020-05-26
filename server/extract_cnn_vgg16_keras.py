#  extract_cnn_vgg16_keras.py
# -*- coding: utf-8 -*-

# keras/tensorflow 使用flask部署服务的常见错误的解决办法
# http://www.luyixian.cn/news_show_381268.aspx
# 非常重要，需要如此才能嵌入flask中使用
# 当前仅能在非dev模式下使用，
# dev会二次load，会有找不到模块的错误。当前没办法解决。

import os

import numpy as np
import tensorflow.compat.v1 as tf  # 这个是需要的
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.backend import set_session
from keras.preprocessing import image
from numpy import linalg

# 下面这些方法是无法运行的
# from tensorflow_core.python.keras.api.keras.preprocessing import image
# from tensorflow_core.python.keras.applications.vgg16 import VGG16, preprocess_input
# from tensorflow_core.python.keras.backend import set_session

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

sess = tf.Session()
graph = tf.get_default_graph()

__all__ = [
    "vgg16_model"
]


class VGGNet:
    def __init__(self):
        set_session(sess)
        # weights: 'imagenet'
        # pooling: 'max' or 'avg'
        # input_shape: (width, height, 3), width and height should >= 48
        self.input_shape = (224, 224, 3)
        self.weight = 'imagenet'
        self.pooling = 'max'
        # include_top：是否保留顶层的3个全连接网络
        # weights：None代表随机初始化，即不加载预训练权重。'imagenet'代表加载预训练权重
        # input_tensor：可填入Keras tensor作为模型的图像输出tensor
        # input_shape：可选，仅当include_top=False有效，应为长为3的tuple，指明输入图片的shape，图片的宽高必须大于48，如(200,200,3)
        # pooling：当include_top = False时，该参数指定了池化方式。None代表不池化，最后一个卷积层的输出为4D张量。‘avg’代表全局平均池化，‘max’代表全局最大值池化。
        # classes：可选，图片分类的类别数，仅当include_top = True并且不加载预训练权重时可用。
        self.model_vgg = VGG16(weights=self.weight,
                               input_shape=(self.input_shape[0], self.input_shape[1], self.input_shape[2]),
                               pooling=self.pooling, include_top=False)
        # with graph.as_default():
        self.model_vgg.predict(np.zeros((1, 224, 224, 3)))

    '''
    Use vgg16/Resnet model to extract features
    Output normalized feature vector
    '''

    # 提取vgg16最后一层卷积特征
    def vgg_extract_feat(self, img_path):
        global sess, graph
        with graph.as_default():
            img = image.load_img(img_path, target_size=(self.input_shape[0], self.input_shape[1]))
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis=0)
            set_session(sess)
            img = preprocess_input(img)
            feat = self.model_vgg.predict(img)
        # print(feat.shape)
        # print(feat[0])
        # print(LA.norm(feat[0]))
        norm_feat = feat[0] / linalg.norm(feat[0])
        return norm_feat

    # 提取vgg16最后一层卷积特征
    def vgg_extract_feat_batch(self, img_path_arr):
        global sess, graph
        set_session(sess)
        imgs = []
        for img_path in img_path_arr:
            img = image.load_img(img_path, target_size=(self.input_shape[0], self.input_shape[1]))
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis=0)
            imgs.append(img)
        with graph.as_default():
            set_session(sess)
            img = np.concatenate([x for x in imgs])
            img = preprocess_input(img)
            # with graph.as_default():
            feat = self.model_vgg.predict(img)
        # print(feat.shape)
        # print(feat[0])
        # print(LA.norm(feat[0]))
        # norm_feat_arr = []
        # for i in xrange(0, feat.shape[0]):
        #     norm_feat = feat[i] / LA.norm(feat[i])
        #     norm_feat_arr.append(norm_feat)
        # return norm_feat_arr
        return feat / linalg.norm(feat)


vgg16_model = VGGNet()
