import re
from urllib.parse import urlparse

import pymysql
from dbutils.pooled_db import PooledDB
from loguru import logger
from pymysql.cursors import DictCursor

from sqlman.tools import *


class Handler:
    def __init__(self, host=None, port=None, username=None, password=None, db=None, **kwargs):
        """
        连接MySQL
        Args:
            host: 地址
            port: 端口
            username: 用户
            password: 密码
            db: 数据库
            **kwargs: 跟PooledDB参数保持一致
        """
        cfg = dict(
            host=host or 'localhost',
            port=port or 3306,
            user=username,
            password=password,
            db=db,
            mincached=1,
            maxcached=20,
            charset='utf8mb4',
            maxconnections=10,
            blocking=True
        )
        cfg.update(kwargs)
        self._cfg = cfg
        self._pool = PooledDB(pymysql, **self._cfg)

    @classmethod
    def from_url(cls, url: str):
        """连接MySQL，地址格式为：mysql://username:password@host:port/db"""
        result = urlparse(url)
        return cls(
            host=result.hostname,
            port=result.port,
            username=result.username,
            password=result.password,
            db=result.path.strip('/')
        )

    def __getitem__(self, name: str):
        assert name in self.get_tables(), f"table <{name}> is not exists"
        from sqlman.table_controller import TableController
        return TableController(self._cfg, name)

    def pick_table(self, name: str):
        """选择表"""
        return self.__getitem__(name)

    @staticmethod
    def panic(sql, msg):
        """错误日志"""
        sql = re.sub("\s+", ' ', sql).strip()
        logger.error(
            """
            sql     {}
            msg     {}
            """.format(sql, msg)
        )

    def open_connect(self, dict_cursor=False):
        """打开连接"""
        con = self._pool.connection()
        cur = con.cursor(DictCursor) if dict_cursor else con.cursor()
        return cur, con

    def close_connect(self, cur, con):
        """关闭连接"""
        if cur:
            cur.close()
        if con:
            con.close()

    def exe_sql(self, sql: str, args=None, query_all=None, to_dict=True, allow_failed=True) -> dict:
        """执行SQL"""
        cur, con = None, None
        try:
            cur, con = self.open_connect(to_dict)
            line = cur.execute(sql, args=args)
            con.commit()
        except Exception as e:
            if allow_failed is False:
                raise e
            self.panic(sql, e)
            return make_result(status=0, error=str(e))
        else:
            query_results = None if query_all is None else list(cur.fetchall()) if query_all else cur.fetchone()
            return make_result(status=1, affect=line, data=query_results)
        finally:
            self.close_connect(cur, con)

    def exem_sql(self, sql: str, args=None) -> int:
        """批量执行SQL"""
        cur, con = None, None
        try:
            cur, con = self.open_connect()
            line = cur.executemany(sql, args=args)
            con.commit()
            return line
        except Exception as e:
            self.panic(sql, e)
            return 0
        finally:
            self.close_connect(cur, con)

    def _insert_one(self, table: str, item: dict, update: str = None, unique_index: str = None) -> int:
        """
        插入数据
        Args:
            table: 表
            item: 数据
            update: 数据重复，则更新数据
            unique_index: 唯一索引

        Returns:
            受影响的行数
        """
        fields, values = getfv(item)
        new = '' if not (update or unique_index) else 'ON DUPLICATE KEY UPDATE {}'.format(
            update or '{}={}'.format(unique_index, unique_index)
        )
        sql = 'insert into {}({}) value({}) {}'.format(table, fields, values, new)
        args = tuple(item.values())
        affect = self.exe_sql(sql, args=args)['affect']
        return affect

    def _insert_many(self, table: str, items: list, update: str = None, unique_index: str = None) -> int:
        """
        批量插入数据
        Args:
            table: 表
            items: 数据
            update: 数据重复，则更新数据
            unique_index: 唯一索引

        Returns:
            受影响的行数
        """
        fields, values = getfv(items)
        new = '' if not (update or unique_index) else 'ON DUPLICATE KEY UPDATE {}'.format(
            update or '{}={}'.format(unique_index, unique_index)
        )
        sql = 'insert into {}({}) value({}) {}'.format(table, fields, values, new)
        args = [tuple(item.values()) for item in items]
        affect = self.exem_sql(sql, args=args)
        return affect

    def get_tables(self) -> list:
        """获取当前数据库的所有表名称"""
        sql = 'show tables'
        data = self.exe_sql(sql, to_dict=False, query_all=True)['data']
        tables = [v[0] for v in data]
        return tables

    def remove_table(self, name: str) -> bool:
        """删除表"""
        sql = 'DROP TABLE {}'.format(name)
        return self.exe_sql(sql)['status'] == 1

    def make_datas(self, table: str, once=1000, total=10000):
        """新增测试表并添加测试数据"""
        import random
        from faker import Faker

        faker = Faker("zh_cn")
        n = 0

        def create_table():
            """新建测试表"""
            sql = '''
                create table {}
                (
                    id          int NOT NULL    AUTO_INCREMENT,
                    name        varchar(20)     DEFAULT NULL,
                    gender      varchar(1)      DEFAULT NULL,
                    age         int(3)          DEFAULT NULL,
                    phone       varchar(11)     DEFAULT NULL,
                    ssn         varchar(18)     DEFAULT NULL,
                    job         varchar(200)    DEFAULT NULL,
                    salary      int(8)          DEFAULT NULL,
                    company     varchar(200)    DEFAULT NULL,
                    address     varchar(200)    DEFAULT NULL,
                    mark        varchar(1)      DEFAULT NULL,
                    primary key (id)
                ) 
                ENGINE=InnoDB    DEFAULT CHARSET=utf8mb4;
            '''.format(table)
            return self.exe_sql(sql)['status']

        def make_item():
            """制造一条数据"""
            item = {
                'name': faker.name(),
                'gender': random.choice(['男', '女']),
                'age': faker.random.randint(18, 60),
                'phone': faker.phone_number(),
                'ssn': faker.ssn(),
                'job': faker.job(),
                'salary': faker.random_number(digits=4),
                'company': faker.company(),
                'address': faker.address(),
                'mark': faker.random_letter()
            }
            return item

        def into_mysql(target, count):
            """数据进入MySQL"""
            items = [make_item() for _ in range(count)]
            line = self._insert_many(target, items, unique_index='id')
            nonlocal n
            n += line
            logger.success('MySQL，插入{}，累计{}'.format(line, n))

        if not create_table():
            return

        if total < once:
            into_mysql(table, total)
            return

        for _ in range(total // once):
            into_mysql(table, once)

        if other := total % once:
            into_mysql(table, other)

        logger.success('新表，{}/{}'.format(self._cfg['db'], table))
