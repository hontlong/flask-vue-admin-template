# encoding=utf8

import milvus
from flask import Blueprint, current_app, g
from flask import render_template

from . import db
from . import idmap
from .hash import *
from .pub import *
from .server_helper import *
from .tables import *

__all__ = [
    'bp'
]

# Python 内置类型 dict，list ，tuple 基础操作是线程安全的，复合操作不是


bp = Blueprint('similar', __name__)


@bp.errorhandler(400)
def param_not_set(error):
    return return_fail(str(error))


@bp.errorhandler(500)
@bp.errorhandler(404)
def page_not_found(error):
    return return_fail(str(error))


# 1. API说明
# 1. 效果展示
@bp.route('/')
def home():
    return render_template('index.html')


algo_dims = {'simhash': 64, 'doc2vec': 100, 'bert': 768, 'vgg16': 512}
algo_metric = {'simhash': milvus.MetricType.HAMMING, 'doc2vec': milvus.MetricType.IP, 'bert': milvus.MetricType.IP,
               'vgg16': milvus.MetricType.IP}


# /admin/api
@bp.route('/table/list', methods=['GET', 'POST'])
def table_list():
    tbls = all_table()
    print(g, id(g))
    print('get table size:', len(tbls))
    ts = [t.info_map() for t in tbls.values()]
    return return_simple_data(ts)


@bp.route('/create', methods=['GET', 'POST'])
def table_create():
    req = parser_req()

    anm = req['anm']
    ctype = req['ctype']
    item_type = req['item_type']
    sim_algo = req['sim_algo']

    table_name = gen_table_name(anm, ctype)
    table = get_table(table_name)
    if table is not None:
        return return_fail("table name {} already exists.".format(table_name))

    table = Table(table_name, item_type, sim_algo)

    dim = algo_dims[sim_algo]
    metric_type = algo_metric[sim_algo]
    nlist = 1024

    client = db.get_milvus_client()
    status = client.create_collection({
        "collection_name": table_name,
        "dimension": dim,
        "metric_type": metric_type,
        "index_file_size": 1024
    })
    if not status.OK():
        msg = "create table %s fail:%s" % (table_name, status.message)
        current_app.logger.error(msg)
        msg = "create table %s fail" % table_name
        return return_fail(msg)

    status = db.get_milvus_client().create_index(table_name, milvus.IndexType.IVF_FLAT, {
        "nlist": nlist,
    })
    if not status.OK():
        msg = "create table %s index fail:%s" % (table_name, status.message)
        current_app.logger.error(msg)
        return_fail(msg)

    table.dim = dim
    table.metric_type = metric_type
    table.index_type = milvus.IndexType.IVF_FLAT
    table.nlist = nlist

    add_table(table)
    tbls = all_table()
    print("set table size:", len(tbls))

    return return_ok()


@bp.route('/insert', methods=['GET', 'POST'])
def table_insert():
    req = parser_req()
    anm = req['anm']
    ctype = req['ctype']
    item_id = req['item_id']
    item = req['item']

    table_name = gen_table_name(anm, ctype)
    table = get_table(table_name)
    if table is None:
        return return_fail("table {} not exists.".format(table_name))

    vec = table.gen_item_vec(item)
    _id = str_2_id(item_id)

    if table.sim_algo == "simhash":
        current_app.logger.debug("_id:%d vec:%s", _id, bytes_to_hexs(vec))
    else:
        tmp_vec = []
        if len(vec) > 4:
            tmp_vec.append(str(vec[0]))
            tmp_vec.append(str(vec[1]))
            tmp_vec.append(str(vec[2]))
            tmp_vec.append('...')
            tmp_vec.append(str(vec[-1]))
        else:
            tmp_vec = vec

        current_app.logger.debug("_id:%d vec:%s", _id, tmp_vec)

    # 验证过，输入的id和返回的id是一致的
    client = db.get_milvus_client()
    status, _ = client.insert(table_name, [vec], ids=[_id])
    if not status.OK():
        msg = "milvus op fail: {}".format(status.message)
        current_app.logger.error(msg)
        return return_fail(msg)

    table.append_id(_id, item_id)
    # idmap.hset(table_name, item_id, item)
    ssdb_client = db.get_redis_client()
    idmap.hset(ssdb_client, table_name, item_id, item)

    return return_ok()


# vec 是单独1个向量，不是元素为1的数组
def _search_by_vec(table, vec, top_n, nprobe=10, need_return_item=False):
    # rss => [][]()
    client = db.get_milvus_client()
    status, rss = client.search(table.name, top_n, [vec], params={
        "nprobe": nprobe
    })

    if not status.OK():
        msg = "milvus op fail: {}".format(status.message)
        return return_fail(msg)

    data = []
    for rs in rss:
        for r in rs:
            dis = r.distance
            metric_type = algo_metric[table.sim_algo]
            if metric_type == milvus.MetricType.HAMMING:
                sim = (64.0 - dis) / 64.0
            else:
                sim = dis
            _id = r.id
            item_id = table.id_map.get(_id, None)
            if item_id is None:
                current_app.logger.warn("can not map id {} to item_id".format(_id))
                continue
            obj = {
                'dis': dis,
                'sim': round(sim, 4),
                'item_id': item_id,
            }
            data.append(obj)
        if need_return_item:
            item_id_arr = []
            for obj in data:
                item_id_arr.append(obj['item_id'])
            redis_client = db.get_redis_client()
            kvmap = idmap.hmget(redis_client, table.name, item_id_arr)
            # print(kvmap)
            for obj in data:
                # obj['item'] = val_arr[idx]
                v = kvmap[obj['item_id']]
                obj['item'] = str(v)
        break  # 仅查询1条

    return return_simple_data(data)


@bp.route('/search', methods=['GET', 'POST'])
def table_search():
    req = parser_req()

    anm = req['anm']
    ctype = req['ctype']
    item = req['item']
    top_n = int(req.get('top_n', '5'))
    need_item = parse_bool(req.get('need_item', ''))

    table_name = gen_table_name(anm, ctype)
    table = get_table(table_name)
    if table is None:
        return return_fail("table {} not exists.".format(table_name))

    vec = table.gen_item_vec(item)

    return _search_by_vec(table, vec, top_n, need_return_item=need_item)


# anm,ctype,item_id
@bp.route('/search_by_id')
def table_search_by_id():
    req = parser_req()

    anm = req['anm']
    ctype = req['ctype']
    item_id = req['item_id']
    top_n = int(req.get('top_n', '5'))
    need_item = parse_bool(req.get('need_item', ''))

    table_name = gen_table_name(anm, ctype)
    table = get_table(table_name)
    if table is None:
        return return_fail("table {} not exists.".format(table_name))

    _id = str_2_id(item_id)
    if _id not in table.id_map:
        msg = "item_id {} not exists, please insert it first.".format(item_id)
        return return_fail(msg)

    client = db.get_milvus_client()
    status, vec = client.get_vector_by_id(table_name, _id)
    if not status.OK():
        msg = "milvus op fail: {}".format(status.message)
        return return_fail(msg)

    return _search_by_vec(table, vec, top_n, need_return_item=need_item)


# @bp.route('/delete')
# def table_delete():
#     anm = request.args['anm']
#     ctype = request.args['ctype']
#     item_id = request.args['item_id']
#
#     table_name = gen_table_name(anm, ctype)
#     table = get_table(table_name)
#     if table is None:
#         return return_fail("table {} not exists.".format(table_name))
#
#     _id = str_2_id(item_id)
#     status = client.delete_by_id(table_name, [_id])
#     if not status.OK():
#         msg = "milvus op fail: {}".format(status.message)
#         return return_fail(msg)
#
#     return return_ok()

@bp.route('/drop')
def table_drop():
    req = parser_req()

    anm = req['anm']
    ctype = req['ctype']

    table_name = gen_table_name(anm, ctype)
    table = get_table(table_name)
    if table is None:
        return return_fail("table {} not exists.".format(table_name))

    client = db.get_milvus_client()
    status = client.drop_collection(table_name)
    if not status.OK():
        msg = 'when drop table {} fail:{}'.format(table_name, status.message)
        current_app.logger.error(msg)
        return return_fail(msg)

    remove_table(table.name)

    redis_client = db.get_redis_client()
    idmap.del_table(redis_client, table.name)

    return return_ok()


# @bp.route('/item', methods=['GET'])
# def table_search_by_id():
#     req = parser_req()
#
#     anm = req['anm']
#     ctype = req['ctype']
#     item_id = req['item_id']
#
#     table_name = gen_table_name(anm, ctype)
#     table = get_table(table_name)
#     if table is None:
#         return return_fail("table {} not exists.".format(table_name))
#
#     rc = db.get_redis_client()
#     b64str = idmap.hget(rc, table_name, item_id)


def gen_table_name(anm, ctype):
    return '%s_%s' % (anm, ctype)


def gen_collection(client, collection_name, dimension, metric_type, index_file_size=1024):
    collection_param = {
        "collection_name": collection_name,
        "dimension": dimension,
        "metric_type": metric_type,
        "index_file_size": index_file_size
    }

    return client.create_collection(collection_param)
