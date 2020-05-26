# encoding=utf8
# 这里的函数应该是可以跨应用的，最好无依赖
import base64
import io
import time

import requests


def line_2_map(line):
    m = {}
    fs = line.split('`')
    for f in fs:
        ss = f.split('=')
        k = ss[0]
        if len(ss) > 1:
            v = ss[1]
        else:
            v = ""
        m[k] = v
    return m


def map_2_line(m):
    fs = []
    for k, v in m.items():
        f = "{}={}".format(k, v)
        fs.append(f)
    return "`".join(fs)


def time_now_str():
    return time.strftime("%Y%m%d_%H%M%S")


# 你好 -> 5L2g5aW9
def base64_encode(string):
    bs = string.encode('utf-8')
    bs = base64.standard_b64encode(bs)
    s = str(bs, 'utf-8')
    return s


# 5L2g5aW9 -> 你好
def base64_decode(string):
    bs = string.encode('utf-8')
    bs = base64.standard_b64decode(bs)
    s = str(bs, 'utf-8')
    return s


def base64_encode_image_fp(img_fp):
    img_fp.seek(0)
    bs = img_fp.read()
    bs = base64.standard_b64encode(bs)
    s = str(bs, 'utf-8')
    return s


def base64_decode_image_fp(string):
    bs = string.encode('utf-8')
    bs = base64.standard_b64decode(bs)
    fd = io.BytesIO(bs)
    return fd


def open_fp_from_url(url):
    """
    打开一个url,file并构建fd对象，此对象可以在pil open中打开
    :param url:
    :return:
    """
    if url.startswith("file://"):
        file_path = url[7:]
        with open(file_path, "rb") as f:
            fd = io.BytesIO(f.read())
            return fd
    r = requests.get(url, timeout=15, stream=True)
    if r.status_code == 200:
        fd = io.BytesIO(r.content)
        return fd
    return None


def hexs_to_bytes(hexs):
    """
    :param hexs: 16进制的字符串  ABCDEF0123456789AB
    :return: bytes 对象 py3
    """
    return bytes.fromhex(hexs)


def bytes_to_hexs(bs):
    return ''.join(['%02X' % b for b in bs])


# py3
def strdecode(sentence):
    if not isinstance(sentence, str):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    return sentence


def parse_bool(s):
    s = str(s).lower().strip()
    false_ks = {'false', '0', 'no', ''}
    if s in false_ks:
        return False
    return True


# 仅用于py3
def strdecode(sentence):
    """
    把字符转为标准的字符，处理编码问题
    :return: 标准化后的字符串
    """
    if not isinstance(sentence, str):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    return sentence
