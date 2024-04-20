# -*- coding: utf-8 -*-

import time

from loguru import logger

from sqlman.handler import Handler


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


class TableController(Handler):
    def __init__(self, cfg: dict, table: str):
        super().__init__(cfg)
        self.table = table

    def delete(self, limit: int = None, **kwargs):
        """删除一条或多条数据"""
        sql = 'delete from {} where {} {}'.format(
            self.table,
            make_condition(kwargs),
            '' if limit is None else 'limit {}'.format(limit)
        )
        return self.exe_sql(sql)

    def update(self, new: dict, limit: int = None, **kwargs):
        """更新数据"""
        sql = 'update {} set {} where {} {}'.format(
            self.table,
            make_update(new),
            make_condition(kwargs),
            '' if limit is None else 'limit {}'.format(limit)
        )
        return self.exe_sql(sql)

    def query(self, pick='*', limit: int = None, **kwargs) -> list:
        """查询数据"""
        sql = 'select {} from {} where {} {}'.format(
            pick,
            self.table,
            make_condition(kwargs),
            '' if limit is None else 'limit {}'.format(limit)
        )
        return self.exe_sql(sql, query_all=True)

    def query_count(self, **kwargs) -> int:
        """查询数量"""
        sql = 'select count(1) from {} {}'.format(
            self.table,
            'where {}'.format(make_condition(kwargs)) if kwargs else ''
        )
        count = self.exe_sql(sql, query_all=False, dict_cursor=False)[0]
        return count

    def is_exists(self, **kwargs) -> bool:
        """查询数据是否存在"""
        sql = 'select 1 from {} where {} limit 1'.format(self.table, make_condition(kwargs))
        return self.exe_sql(sql) == 1

    def random(self, limit=1) -> dict | list:
        """随机返回一条或多条数据"""
        sql = 'select * from {} where id >= (rand() * (select max(id) from {})) limit {}'.format(
            self.table,
            self.table,
            limit
        )
        datas = self.exe_sql(sql, query_all=True if limit > 1 else False)
        return datas

    @staticmethod
    def items_is_ok(items: list, must_exist: str) -> bool:
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
                if must_exist not in fields:
                    return False
                if fields != set(item):
                    return False
        return True

    def update_one(self, item: dict, depend: str) -> int:
        """
        更新数据
        Args:
            item: 数据，且含有<depend>字段
            depend: 条件判断的字段

        Returns:
            受影响的行数
        """
        dv = item.pop(depend)
        temp = []
        args = []
        for k, v in item.items():
            temp.append('{}=%s'.format(k))
            args.append(v)
        s = ', '.join(temp)
        args.append(dv)
        sql = 'update {} set {} where {}=%s'.format(self.table, s, depend)
        return self.exe_sql(sql, args=args)

    def update_many(self, items: list, depend: str) -> int:
        """
        批量更新数据
        Args:
            items: 多条数据，每条数据含有<depend>字段
            depend: 条件判断的字段

        Returns:
            受影响的行数
        """
        assert self.items_is_ok(items, depend), '错误的items'

        ks = list(items[0].keys())
        ks.remove(depend)
        mid = ', '.join(['{}=%s'.format(k) for k in ks])
        sql = 'update {} set {} where {}=%s'.format(self.table, mid, depend)
        args = []
        for one in items:
            vs = [one[k] for k in ks]
            vs.append(one[depend])
            args.append(vs)
        return self.exem_sql(sql, args)

    def update_some(self, items: list, depend: str) -> int:
        """批量更新，只执行了1条SQL"""
        assert self.items_is_ok(items, depend), '错误的items'

        keys = list(items[0].keys())
        keys.remove(depend)

        head = 'update {} set'.format(self.table)

        mid = ''
        args = []
        for key in keys:
            mid += '\t{} = case {}\n\t'.format(key, depend)
            for data in items:
                mid += 'when %s then %s '
                args.append(data[depend])
                args.append(data[key])
            else:
                mid += 'end,\n'
        mid = mid[:-2]

        values = ["'{}'".format(data[depend]) for data in items]
        tail = 'where {} in ({})'.format(depend, ', '.join(values))

        sql = '\n'.join([head, mid, tail])
        return self.exe_sql(sql, args=args)

    def get_min(self, field: str):
        """获取字段的最小值"""
        sql = 'select min({}) from {}'.format(field, self.table)
        value = self.exe_sql(sql, query_all=False, dict_cursor=False)[0]
        return value

    def get_max(self, field: str):
        """获取字段的最大值"""
        sql = 'select max({}) from {}'.format(field, self.table)
        value = self.exe_sql(sql, query_all=False, dict_cursor=False)[0]
        return value

    def scan(
            self, sort_field='id', pick='*',
            start: int = None, end: int = None,
            dealer=None, add_cond=None,
            once=1000, rest=0.05,
            max_query_times=None, log=True
    ):
        """
        扫描数据，每一批数据可以交给回调函数处理
        Args:
            sort_field: 进行排序的字段（数值型、有索引）
            pick: 查询哪些字段
            start: 排序字段的最小值
            end: 排序字段的最大值
            add_cond: 补充的SQL条件
            once: 每一批查询多少条
            rest: 每一批查询的间隔
            dealer: 每一批数据的回调函数
            log: 是否输出查询日志
            max_query_times: 最大查询次数
        """

        times = 0  # 查询了多少次
        dealer = dealer or show_datas  # 具体的回调函数
        start, end = start or self.get_min(sort_field), end or self.get_max(sort_field)  # 查询区间

        first_query = True  # 第一次查询
        while True:
            symbol, cond = '>=' if first_query else '>', '' if add_cond is None else 'and ' + add_cond
            sql = '''
                select {} from {}
                where {} {} {} and {} <= {} {}
                order by {}
                limit {}
            '''.format(
                pick, self.table,
                sort_field, symbol, start, sort_field, end, cond,
                sort_field,
                once
            )

            result: list = self.exe_sql(sql, query_all=True)
            if result is False:
                self.panic(sql, '执行失败')
                return
            if not result:
                self.panic(sql, '查询为空')
                return

            # 输出查询日志
            if log is True:
                params = sort_field, symbol, start, once, len(result), result[0][sort_field], result[-1][sort_field]
                logger.info('{}{}{}  期望{}得到{}  具体{}到{}'.format(*params))

            # 查询出来的数据交给回调函数处理
            if len(result) == once:
                dealer(result)
                start = result[-1][sort_field]
                if start == end:
                    break
            else:
                dealer(result)
                break

            times += 1
            if max_query_times and times >= max_query_times:  # 达到最大查询次数了
                break

            first_query = False
            time.sleep(rest)  # 每一轮查询之间的间隔

    def insert_data(self, data: dict | list | tuple, update: str = None, unique_index: str = None) -> int:
        """批量插入数据"""
        if isinstance(data, dict):
            return super()._insert_one(self.table, data, update, unique_index)
        return super()._insert_many(self.table, list(data), update, unique_index)

    def view_field_values(self, field: str, values: list) -> tuple:
        """
        查看字段的一些值
        Args:
            field: 字段
            values: 一些值

        Returns:
            (不存在的一些值，已存在的一些值)
        """
        datas = self.query(pick=field, **{field: values})
        old = [data[field] for data in datas]
        new = list(set(values) - set(old))
        return new, old

    def dedup_insert_data(self, items: list, dedup_field: str) -> int:
        """
        批量插入数据\n
        如果数据跟数据库中重复，则自动过滤掉
        Args:
            items: 这些数据
            dedup_field: 需要去重的字段

        Returns:
            受影响的行数
        """
        values = [v[dedup_field] for v in items]
        new, exists = self.view_field_values(dedup_field, values)
        items2 = [v for v in items if v[dedup_field] in new]
        return self.insert_data(items2, unique_index=dedup_field) if items2 else 0
