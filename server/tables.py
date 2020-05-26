# encoding=utf8
import os
import threading

from . import db
from .extract_cnn_vgg16_keras import vgg16_model
from .hash import str_2_id
from .log import log
from .pub import *
from .simbert import BertModel

__all__ = [
    "init",
    "Table",
    "all_table",
    "get_table",
    "remove_table",
    "add_table"
]

# 用于避免 save_table_info时的多线程冲突
_tabs_lock = threading.Lock()
sim_algo_set = {'simhash', 'doc2vec', 'bert', 'vgg16'}


def all_table():
    return g_tables


class Table:
    def __init__(self, name, item_type, sim_algo):
        self.name = name
        self.item_type = item_type
        self.sim_algo = sim_algo
        self.doc2vec_model = None
        self.item_id_file = None
        self.bert_model = None
        self.id_map = {}

        global g_data_path
        data_path = g_data_path
        self.data_path = data_path

        if sim_algo not in sim_algo_set:
            raise Exception("unsupport algo {}".format(sim_algo))
        if sim_algo == "doc2vec":
            init_doc2vec_qieci(data_path)
            from .doc_similar_by_doc2vec import load_model
            model_file = '{}/{}.doc2vec_model.bin'.format(data_path, name)
            if not os.path.exists(model_file):
                raise Exception("algo {} must have model file.".format(sim_algo))
            model = load_model(model_file)
            log.info("load model finish")
            self.doc2vec_model = model

        if sim_algo == "bert":
            from . import db
            self.bert_model = BertModel(lambda: db.get_bert_client())

        if sim_algo == "vgg16":
            self.vgg16_model = vgg16_model

            # id map
        item_id_file = "{}/{}.item_id.list.txt".format(data_path, name)
        if os.path.exists(item_id_file):
            with open(item_id_file, "r+", encoding="utf8") as f:
                for line in f:
                    item_id = line.strip()
                    _id = str_2_id(item_id)
                    self.id_map[_id] = item_id
        self.item_id_file = open(item_id_file, "a+")

        log.info("table %s total item size %d" % (name, len(self.id_map)))

    def info_map(self):
        return {
            "table_name": self.name,
            "item_type": self.item_type,
            "sim_algo": self.sim_algo
        }

    def gen_item_vec(self, item):
        # text = "test 测试 कसौटी الاختبار"
        if self.sim_algo == "simhash":
            from .doc_similar_by_simhash import gen_simhash
            text = base64_decode(item)
            sim_hex = gen_simhash(text)
            bs = hexs_to_bytes(sim_hex)
            return bs

        if self.sim_algo == "doc2vec":
            from .doc_similar_by_doc2vec import gen_doc_embedding
            text = base64_decode(item)
            vec = gen_doc_embedding(self.doc2vec_model, text)
            return vec.tolist()

        if self.sim_algo == "bert":
            text = base64_decode(item)
            vec = self.bert_model.gen_doc_embedding(text)
            return vec.tolist()

        if self.sim_algo == "vgg16":
            # TODO
            img_fp = base64_decode_image_fp(item)
            vec = self.vgg16_model.vgg_extract_feat(img_fp)
            img_fp.close()
            return vec.tolist()

    def append_id(self, _id, item_id):
        self.id_map[_id] = item_id
        self.item_id_file.write(item_id)
        self.item_id_file.write('\n')
        self.item_id_file.flush()

    def remove(self):
        """
        对表自己占用资源的清理
        :return: None
        """
        if self.item_id_file:
            try:
                self.item_id_file.close()
            except Exception:
                pass

        item_id_file = "{}/{}.item_id.list.txt".format(self.data_path, self.name)
        if os.path.exists(item_id_file):
            try:
                os.remove(item_id_file)
            except Exception:
                pass


def get_table(table_name):
    return g_tables.get(table_name, None)


def remove_table(table_name):
    global g_data_path
    data_path = g_data_path

    if table_name not in g_tables:
        log.info("%s not in g_tables" % table_name)
        return

    g_tables[table_name].remove()
    del g_tables[table_name]

    save_tables(data_path)


g_already_load_qieci = False


def init_doc2vec_qieci(data_path):
    global g_already_load_qieci
    if g_already_load_qieci:
        return
    from .doc_similar_by_doc2vec import global_config
    user_dict_file = "{}/userdict.txt".format(data_path)
    stop_word_file = "{}/stopwords.txt".format(data_path)
    if os.path.exists(user_dict_file):
        global_config(user_dict_file=user_dict_file)

    if os.path.exists(stop_word_file):
        global_config(stop_word_file=stop_word_file)
    g_already_load_qieci = True


# 仅在初始化时加载1次，不需要锁
def load_tables():
    """
    初始化时的加载
    :return: Table obj List
    """
    data_path = g_data_path

    tables = {}

    tables_file_path = "%s/tables.list.txt" % data_path
    if os.path.exists(tables_file_path):
        with open(tables_file_path, "r+", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                m = line_2_map(line)
                table_name = m['table_name']
                item_type = m['item_type']
                sim_algo = m['sim_algo']
                table = Table(table_name, item_type, sim_algo)
                tables[table_name] = table
    return tables


def save_tables(data_path):
    def _inner():
        tables = []
        for tab in g_tables.values():
            m = {
                "table_name": tab.name,
                "item_type": tab.item_type,
                "sim_algo": tab.sim_algo
            }
            tables.append(m)

        tables_file_path = "%s/tables.list.txt" % data_path
        if os.path.exists(tables_file_path):
            bak_path = "%s.%s" % (tables_file_path, time_now_str())
            log.info("bak tables file: %s -> %s" % (tables_file_path, bak_path))
            os.rename(tables_file_path, bak_path)

        if tables:
            with open(tables_file_path, "w+", encoding="utf-8") as f:
                for m in tables:
                    line = map_2_line(m)
                    f.write(line)
                    f.write('\n')

    with _tabs_lock:
        _inner()


# collection_info CollectionInfo(count: 0, partitions_stat: [PartitionStat(tag: '_default', count: 0, segments_stat: [])])
# describe_collection CollectionSchema(collection_name='example_collection_', dimension=128, index_file_size=32, metric_type=<MetricType: L2>)
# desc_index (collection_name='example_collection_', index_type=<IndexType: IVFLAT>, params={'nlist': 2048})
def check_table_info(milvus_client, tables):
    _, cs = milvus_client.show_collections()
    log.debug("milvus collections:{}".format(cs))
    coll_set = set(cs)
    for table in tables.values():
        if table.name not in coll_set:
            raise Exception("table %s not exists in milvus" % table.name)

        # 收集table其它的 milvus 相关的信息
        _, info = milvus_client.collection_info(table.name)
        if info.count != len(table.id_map):
            msg = "item size not eq, id size %d != milvus item size %d." % (len(table.id_map), info.count)
            log.warning(msg)

        status, desc = milvus_client.describe_collection(table.name)
        if not status.OK():
            msg = "desc collection %s fail: %s." % (table.name, status.message)
            log.warning(msg)
            continue

        table.dim = desc.dimension
        table.metric_type = desc.metric_type

        status, desc = milvus_client.describe_index(table.name)
        if not status.OK():
            msg = "desc collection %s index fail: %s." % (table.name, status.message)
            log.warning(msg)
            continue
        table.index_type = desc.index_type
        table.nlist = int(desc.params['nlist'])


def add_table(table):
    """
    同步一个table信息到文件 append
    """
    data_path = g_data_path

    def _inner():
        g_tables[table.name] = table
        tables_file_path = "%s/tables.list.txt" % data_path
        with open(tables_file_path, "a+", encoding="utf-8") as f:
            m = table.info_map()
            line = map_2_line(m)
            f.write(line)
            f.write('\n')
            f.flush()

    with _tabs_lock:
        _inner()
        print('add table size:', len(g_tables))


# 仅在初始化时调用1次
def init(data_path):
    global g_data_path
    global g_tables

    g_data_path = data_path
    tables = load_tables()

    milvus_client = db.get_milvus_client()
    check_table_info(milvus_client, tables)
    g_tables = tables


g_tables = {}
g_data_path = "./data"
