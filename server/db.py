# init_tables(app.config['DATA_PATH'], client)
# idmap.init(app.config['IDMAP_SSDB_HOST'], int(app.config['IDMAP_SSDB_PORT']))

import milvus
import redis
from flask import current_app
from flask import g

from . import log


def get_milvus_client():
    if 'milvus_client' not in g:
        client = milvus.Milvus(uri=current_app.config['MILVUS_URI'])
        if not client.connected():
            log.error("can not connect milvus:%s" % current_app.config['MILVUS_URI'])
            exit(-1)
        g.milvus_client = client
    return g.milvus_client


def get_redis_client():
    if 'redis_client' not in g:
        g.redis_client = redis.Redis(host=current_app.config['REDIS_HOST'], port=current_app.config['REDIS_PORT'])
    return g.redis_client


def get_bert_client():
    if 'bert_client' not in g:
        from bert_serving.client import BertClient
        app = current_app
        conf = app.config
        host = conf['BERT_SERVICE_HOST']
        port = conf['BERT_SERVICE_PORT']
        port_out = conf['BERT_SERVICE_PORT_OUT']
        timeout = 5 * 1000  # ms
        client = BertClient(ip=host, port=port, port_out=port_out, output_fmt='ndarray', timeout=timeout)
        g.bert_client = client

    return g.bert_client


def close_client(e=None):
    def close(name):
        client = g.pop(name, None)
        if client is not None:
            try:
                if hasattr(client, 'close'):
                    client.close()
            except Exception:
                pass

    close('milvus_client')
    close('bert_client')
    close('redis_client')
