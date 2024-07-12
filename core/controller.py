import time

from dbutils.pooled_db import PooledDB
from loguru import logger

from sqlman.core.connector import Connector
from sqlman.tools import make_set, make_where, make_tail, check_items, print_lines


class Controller(Connector):
    """表格控制者"""

    def __init__(self, name: str, pool: PooledDB, cfg: dict):
        self.name = "`{}`".format(name)
        self._pool = pool
        self._cfg = cfg

    def remove(self) -> bool:
        """删除这张表"""
        return self.remove_table(self.name)

    def delete(self, limit: int = None, **kwargs) -> int:
        """
        删除数据（默认删除所有数据）\n
        注意：请限定条件进行删除
        """
        _sql = "delete from {} {}"
        _where, _args = make_where(kwargs)
        tail = make_tail(_where, limit)
        sql = _sql.format(self.name, tail)
        affect = self.exe_sql(sql, args=_args)["affect"]
        return affect

    def update(self, new: dict, limit: int = None, **kwargs) -> int:
        """更新数据"""
        _sql = "update {} set {} {}"
        _set, args1 = make_set(new)
        _where, args2 = make_where(kwargs)
        tail = make_tail(_where, limit)
        args = args1 + args2
        sql = _sql.format(self.name, _set, tail)
        affect = self.exe_sql(sql, args=args)["affect"]
        return affect

    def query(self, pick='*', limit: int = None, **kwargs) -> list:
        """查询数据"""
        if pick != '*' and pick.find(',') != -1:
            pick = ', '.join(["`{}`".format(f.strip().strip('`')) for f in pick.split(',') if f.strip()])
        _sql = "select {} from {} {}"
        _where, args = make_where(kwargs)
        tail = make_tail(_where, limit)
        sql = _sql.format(pick, self.name, tail)
        data = self.exe_sql(sql, args=args, query_all=True)["data"]
        return data

    def query_count(self, **kwargs) -> int:
        """查询数量"""
        _sql = "select count(1) from {} {}"
        _where, args = make_where(kwargs)
        tail = make_tail(_where)
        sql = _sql.format(self.name, tail)
        count = self.exe_sql(sql, args=args, query_all=False)["data"]["count(1)"]
        return count

    def exists(self, **kwargs) -> bool:
        """检查数据是否存在"""
        _where, args = make_where(kwargs)
        sql = 'select 1 from {} where {} limit 1'.format(self.name, _where)
        return self.exe_sql(sql, args=args)['affect'] == 1

    def random(self, limit=1) -> dict | list:
        """随机返回一条或多条数据"""
        sql = 'select * from {} where id >= (rand() * (select max(id) from {})) limit {}'.format(
            self.name,
            self.name,
            limit
        )
        data = self.exe_sql(sql, query_all=limit)['data']
        return data

    def update_one(self, item: dict, depend: str) -> int:
        """
        更新

        Args:
            item: 数据，且含有<depend>字段
            depend: 条件判断的字段

        Returns:
            已更新的行数
        """
        dv = item.pop(depend)
        temp = []
        args = []
        for k, v in item.items():
            temp.append('{}=%s'.format(k))
            args.append(v)
        s = ', '.join(temp)
        args.append(dv)
        sql = 'update {} set {} where {}=%s'.format(self.name, s, depend)
        affect = self.exe_sql(sql, args=args)['affect']
        return affect

    def update_many(self, items: list, depend: str) -> int:
        """
        批量更新

        Args:
            items: 多条数据，每条数据含有<depend>字段
            depend: 条件判断的字段

        Returns:
            已更新的行数
        """
        check_items(items, depend)

        ks = list(items[0].keys())
        ks.remove(depend)
        mid = ', '.join(['{}=%s'.format(k) for k in ks])
        sql = 'update {} set {} where {}=%s'.format(self.name, mid, depend)
        args = []
        for one in items:
            vs = [one[k] for k in ks]
            vs.append(one[depend])
            args.append(vs)
        affect = self.exem_sql(sql, args)
        return affect

    def update_some(self, items: list, depend: str) -> int:
        """批量更新，只执行了1条SQL"""
        check_items(items, depend)

        keys = list(items[0].keys())
        keys.remove(depend)

        head = 'update {} set'.format(self.name)

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
        affect = self.exe_sql(sql, args=args)['affect']
        return affect

    def get_min(self, field: str):
        """获取字段的最小值"""
        sql = 'select min({}) from {}'.format(field, self.name)
        min_value = self.exe_sql(sql, query_all=False, to_dict=False)['data'][0]
        return min_value

    def get_max(self, field: str):
        """获取字段的最大值"""
        sql = 'select max({}) from {}'.format(field, self.name)
        max_value = self.exe_sql(sql, query_all=False, to_dict=False)['data'][0]
        return max_value

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
        dealer = dealer or print_lines  # 具体的回调函数
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
                pick, self.name,
                sort_field, symbol, start, sort_field, end, cond,
                sort_field,
                once
            )

            result: list = self.exe_sql(sql, query_all=True)['data']
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

    def insert_data(self, data: dict | list, update: str = None, unique: str = None) -> int:
        """
        插入数据，dict插入一条，list插入多条

        Args:
             data: {} | [{}, {}, {}]
             update: 更新
             unique: 唯一索引

        Returns:
            已插入的行数
        """
        if isinstance(data, dict):
            return super()._add_one(self.name, data, update, unique)
        return super()._add_many(self.name, list(data), update, unique)

    def cvs(self, field: str, values: list) -> tuple:
        """
        检查字段的多个值

        Args:
            field: 字段
            values: 多个值

        Returns:
            (不存在的一些值，已存在的一些值)
        """
        data = self.query(pick=field, **{field: values})
        old = [one[field] for one in data]
        new = list(set(values) - set(old))
        return new, old

    def dedup_insert_data(self, items: list, dedup: str) -> int:
        """
        去重版插入数据

        Args:
            items: [{}, {}, {}]
            dedup: 进行去重的字段

        Returns:
            已插入的行数
        """
        vs = [item[dedup] for item in items]
        nv, ov = self.cvs(field=dedup, values=vs)
        items2 = [a for a in items if a[dedup] in nv]
        return self.insert_data(items2, unique=dedup) if items2 else 0
