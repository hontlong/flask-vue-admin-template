# flask
# SECRET_KEY =  #线上启动时，设置一个随机数

# app
DATA_PATH = "./data"

MILVUS_HOST = 'test-sg-reco-test-001'
MILVUS_PORT = 19530
MILVUS_URI = 'tcp://%s:%d' % (MILVUS_HOST, MILVUS_PORT)

REDIS_HOST = "test-sg-reco-test-001"
REDIS_PORT = 9221

BERT_SERVICE_HOST = 'test-sg-reco-test-001'
BERT_SERVICE_PORT = 5555
BERT_SERVICE_PORT_OUT = 5556
