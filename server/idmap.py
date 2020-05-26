# id mapping
# ssdb : redis
# kv
# key= ${table_name}`${item_id}
# val= ${type}`${content}
#   1. type=raw
#   2. type=b64
#   3. type=url
# k hash
# key = table_name
# field = item_id
# value = val

# import redis

# https://blog.csdn.net/u012851870/article/details/44754509
# http://ssdb.io/docs/zh_cn/redis-to-ssdb.html
# http://ssdb.io/docs/zh_cn/php/

__all__ = [
    "hset",
    "hmget",
    "del_table"
]


def hset(client, table, item_id, val):
    client.hset(table, item_id, val)


def hget(client, table, item_id):
    v = client.hget(table, item_id)
    s = ""
    if v:
        s = v.decode('utf-8')
    return s


# def hmset(client, table, item_id_val_map):
#     client.multi_hset(table, item_id_val_map)


def hmget(client, table, item_id_arr):
    """
    :return map{k,v}
    """
    vs = client.hmget(table, item_id_arr)
    kv_map = {}
    for i in range(0, len(vs), 1):
        k = item_id_arr[i]
        v = vs[i].decode('utf-8')
        kv_map[k] = v
    return kv_map


def del_table(client, table):
    client.delete(table)
