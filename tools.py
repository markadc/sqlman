# -*- coding: utf-8 -*-

def get(key: str):
    def outer(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs).get(key)

        return inner

    return outer


def build_result(**kwargs) -> dict:
    result = dict(**kwargs)
    return result


def make_update(data: dict) -> str:
    """set部分"""
    return ', '.join(["`{}`='{}'".format(k, v) for k, v in data.items()])


def add_quotation(some: list) -> str:
    """['a', 'b', 'c']  ==>  'a','b','c'"""
    res = ', '.join(["'{}'".format(v) for v in some])
    return res


def make_condition(data: dict) -> str:
    """where部分"""
    where = ' and '.join(
        [
            f'`{k}` in ({add_quotation(v)})' if isinstance(v, list) else f"`{k}`='{v}'"
            for k, v in data.items()
        ]
    )
    return where


def show_datas(datas: list):
    """仅配合scan"""
    for data in datas:
        print(data)


def ensure_safe(items: list, must_exist: str):
    """
    校验items，item结构一致且含有<must_exist>字段
    Args:
        items: 一些数据
        must_exist: 必须存在的字段
    """
    fields = None
    for item in items:
        if fields is None:
            fields = set(item)
        else:
            assert must_exist in fields, f'缺失字段{must_exist}'
            assert fields == set(item), '结构不一致'
