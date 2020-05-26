# 均值漂移聚类
# K-Medians的优势是使用中位数来计算中心点不受异常值的影响
# https://blog.csdn.net/Katherine_hsr/article/details/79382249?utm_medium=distribute.pc_relevant.none-task-blog-baidujs-4
# sklearn 中的聚类方法的使用 https://blog.csdn.net/qq_40587575/article/details/82694170
import numpy as np
import sklearn.cluster as sc

# 读取数据，绘制图像
x = np.loadtxt('../data/_vecs.list.txt', unpack=False, dtype='float32', delimiter=',')
print(x.shape)


def cluste(x, algo, params):
    """
    聚类
    :param x: 向量 numpy array
    :param algo: 算法名
    :param params: 参数 dict 所有字母小写，没有下划线中划线
    :return: 标签数组 [] 维度同 x
    """
    if algo == "kmeans":
        model = sc.KMeans(n_clusters=params["nclusters"])
    elif algo == "agglomerative":
        model = sc.AgglomerativeClustering(n_clusters=params["nclusters"])
    else:
        # raise Exception("unsupport algo:%s" % algo)
        model = sc.SpectralClustering()
    labels = model.fit_predict(x)
    return labels
