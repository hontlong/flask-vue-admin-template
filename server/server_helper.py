import json

from flask import request


def return_fail(msg):
    return {
        'status': 0,
        'msg': msg or "unexcept error"
    }


def return_ok():
    return {
        'status': 1
    }


def return_simple_data(data):
    return {
        'status': 1,
        'data': data
    }


def parser_req():
    """
    只有2中方式：GET POST, 如果为POST方式，必须是 json.loads(request.data)
    """
    if request.method == 'GET':
        return request.args

    if request.method == 'POST':
        if request.data:
            param = json.loads(request.data)
        else:
            param = {}
        param.update(request.args)
        return param
