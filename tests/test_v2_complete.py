"""
SQLMan V2 完整测试套件
测试 core/v2 的所有核心功能

运行方式：
    python -m sqlman.tests.test_v2_complete
    或
    cd sqlman/tests && python test_v2_complete.py

注意：需要配置 MySQL 连接信息
"""

import sys
from pathlib import Path

# 支持直接运行
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlman.core.v2 import MySQL, Table

# 导入统一配置
try:
    from .test_config import MYSQL_CONFIG, MYSQL_URL
except ImportError:
    try:
        from test_config import MYSQL_CONFIG, MYSQL_URL
    except ImportError:
        print("⚠️  未找到 test_config.py，请先创建配置文件")
        print("   可以复制 test_config_example.py 为 test_config.py 并修改配置")
        sys.exit(1)


class TestConfig:
    """测试配置"""
    MYSQL_CONF = MYSQL_CONFIG
    MYSQL_URL = MYSQL_URL


class TestV2MySQL:
    """测试 MySQL 类的功能"""
    
    def __init__(self):
        self.db = None
        self.test_table_name = 'test_users'
    
    def setup(self):
        """初始化连接"""
        print("\n" + "="*80)
        print("🚀 开始测试 MySQL 类")
        print("="*80)
        
        # 测试方式1：字典配置
        print("\n✅ 测试1：字典配置连接")
        try:
            self.db = MySQL(**TestConfig.MYSQL_CONF)
            print(f"   连接成功：{TestConfig.MYSQL_CONF['host']}:{TestConfig.MYSQL_CONF['port']}")
        except Exception as e:
            print(f"   ❌ 连接失败：{e}")
            return False
        return True
    
    def test_from_url(self):
        """测试 URL 连接方式"""
        print("\n✅ 测试2：URL 连接方式")
        try:
            db2 = MySQL.from_url(TestConfig.MYSQL_URL)
            tables = db2.get_tables()
            print(f"   URL 连接成功，当前数据库有 {len(tables)} 张表")
        except Exception as e:
            print(f"   ⚠️  URL 连接测试跳过：{e}")
    
    def test_get_tables(self):
        """测试获取表列表"""
        print("\n✅ 测试3：获取表列表")
        tables = self.db.get_tables()
        print(f"   当前数据库有 {len(tables)} 张表")
        if tables:
            print(f"   表列表前5个：{tables[:5]}")
    
    def test_create_test_table(self):
        """测试创建测试表"""
        print("\n✅ 测试4：创建测试表")
        try:
            # 删除旧表（如果存在）
            if self.test_table_name in self.db.get_tables():
                self.db.remove_table(self.test_table_name)
                print(f"   已删除旧表：{self.test_table_name}")
            
            # 创建新表并填充数据
            table = self.db.gen_test_table(self.test_table_name, once=100, total=500)
            print(f"   ✓ 成功创建测试表：{self.test_table_name}，并插入 500 条数据")
            return table
        except Exception as e:
            print(f"   ❌ 创建测试表失败：{e}")
            return None
    
    def test_pick_table(self):
        """测试获取表对象"""
        print("\n✅ 测试5：获取表对象")
        
        # 方式1：索引方式
        table1 = self.db[self.test_table_name]
        print(f"   方式1 [索引]：{type(table1).__name__}")
        
        # 方式2：pick_table 方式
        table2 = self.db.pick_table(self.test_table_name)
        print(f"   方式2 [方法]：{type(table2).__name__}")
        
        return table1
    
    def run_all(self):
        """运行所有测试"""
        if not self.setup():
            print("\n❌ 初始化失败，测试中止")
            return None
        
        self.test_from_url()
        self.test_get_tables()
        table = self.test_create_test_table()
        self.test_pick_table()
        
        print("\n" + "="*80)
        print("✅ MySQL 类测试完成")
        print("="*80)
        
        return table


class TestV2Table:
    """测试 Table 类的功能"""
    
    def __init__(self, table: Table):
        self.table = table
        self.test_data = []
    
    def test_query_count(self):
        """测试查询数量"""
        print("\n" + "="*80)
        print("🚀 开始测试 Table 查询功能")
        print("="*80)
        
        print("\n✅ 测试1：查询总数量")
        count = self.table.query_count()
        print(f"   表中共有 {count} 条数据")
        return count
    
    def test_query_basic(self):
        """测试基本查询"""
        print("\n✅ 测试2：基本查询")
        
        # 查询所有字段
        data1 = self.table.query(limit=3)
        print(f"   查询前3条（所有字段）：得到 {len(data1)} 条")
        if data1:
            print(f"   示例数据：{data1[0]}")
        
        # 查询指定字段
        data2 = self.table.query(pick='id, name, age', limit=3)
        print(f"   查询前3条（指定字段）：得到 {len(data2)} 条")
        if data2:
            print(f"   示例数据：{data2[0]}")
        
        # 条件查询
        data3 = self.table.query(age=25, limit=5)
        print(f"   条件查询（age=25）：得到 {len(data3)} 条")
        
        return data1
    
    def test_query_in(self):
        """测试 IN 查询"""
        print("\n✅ 测试3：IN 查询")
        
        data = self.table.query(age=[25, 30, 35], limit=10)
        print(f"   IN 查询（age in [25,30,35]）：得到 {len(data)} 条")
        if data:
            ages = [d['age'] for d in data]
            print(f"   年龄分布：{set(ages)}")
    
    def test_exists(self):
        """测试数据存在性检查"""
        print("\n✅ 测试4：检查数据存在性")
        
        # 获取第一条数据
        first = self.table.query(limit=1)
        if first:
            first_id = first[0]['id']
            exists = self.table.exists(id=first_id)
            print(f"   检查 id={first_id} 是否存在：{exists}")
        
        # 检查不存在的数据
        exists2 = self.table.exists(id=999999)
        print(f"   检查 id=999999 是否存在：{exists2}")
    
    def test_random(self):
        """测试随机查询"""
        print("\n✅ 测试5：随机查询")
        
        # 随机一条
        one = self.table.random()
        # random(limit=1) 实际返回的是 list，不是 dict
        if one and isinstance(one, (list, tuple)) and len(one) > 0:
            print(f"   随机1条：id={one[0].get('id') if isinstance(one[0], dict) else None}")
        else:
            print(f"   随机1条：无数据")
        
        # 随机多条
        many = self.table.random(limit=5)
        print(f"   随机5条（返回 list）：得到 {len(many) if many else 0} 条")
    
    def test_get_min_max(self):
        """测试获取最小/最大值"""
        print("\n✅ 测试6：获取字段最小/最大值")
        
        min_id = self.table.get_min('id')
        max_id = self.table.get_max('id')
        print(f"   ID 范围：{min_id} ~ {max_id}")
        
        min_age = self.table.get_min('age')
        max_age = self.table.get_max('age')
        print(f"   年龄范围：{min_age} ~ {max_age}")
    
    def test_insert_single(self):
        """测试单条插入"""
        print("\n" + "="*80)
        print("🚀 开始测试 Table 插入功能")
        print("="*80)
        
        print("\n✅ 测试7：单条插入")
        
        data = {
            'name': '测试用户1',
            'gender': '男',
            'age': 28,
            'phone': '13800138000',
            'job': '测试工程师'
        }
        
        affect = self.table.insert_data(data)
        print(f"   插入1条数据，影响行数：{affect}")
        self.test_data.append(data)
    
    def test_insert_batch(self):
        """测试批量插入"""
        print("\n✅ 测试8：批量插入")
        
        data = [
            {'name': '测试用户2', 'gender': '女', 'age': 25, 'phone': '13800138001', 'job': '产品经理'},
            {'name': '测试用户3', 'gender': '男', 'age': 30, 'phone': '13800138002', 'job': '设计师'},
            {'name': '测试用户4', 'gender': '女', 'age': 27, 'phone': '13800138003', 'job': '运营'},
        ]
        
        affect = self.table.insert_data(data)
        print(f"   插入 {len(data)} 条数据，影响行数：{affect}")
        self.test_data.extend(data)
    
    def test_insert_with_conflict(self):
        """测试冲突处理"""
        print("\n✅ 测试9：插入冲突处理")
        
        # 先插入一条数据
        data = {'id': 99999, 'name': '冲突测试', 'age': 20}
        self.table.insert_data(data, unique='id')
        print(f"   首次插入：id=99999")
        
        # 再次插入相同ID（使用 unique 参数忽略冲突）
        data2 = {'id': 99999, 'name': '冲突测试2', 'age': 21}
        affect = self.table.insert_data(data2, unique='id')
        print(f"   重复插入（unique='id'）：影响行数 {affect}")
        
        # 使用 update 参数在冲突时更新
        data3 = {'id': 99999, 'name': '冲突测试3', 'age': 22}
        affect2 = self.table.insert_data(data3, update='age=age+1')
        print(f"   冲突时更新（update='age=age+1'）：影响行数 {affect2}")
        
        # 验证结果
        result = self.table.query(id=99999)
        if result:
            print(f"   最终数据：age={result[0]['age']} (应该是21)")
    
    def test_dedup_insert(self):
        """测试去重插入"""
        print("\n✅ 测试10：去重插入")
        
        # 准备数据（包含重复的 phone）
        data = [
            {'name': '去重1', 'phone': '13900000001', 'age': 25},
            {'name': '去重2', 'phone': '13900000002', 'age': 26},
            {'name': '去重3', 'phone': '13800138000', 'age': 27},  # 这个 phone 已存在
        ]
        
        affect = self.table.dedup_insert_data(data, dedup='phone')
        print(f"   去重插入 {len(data)} 条，实际插入 {affect} 条（自动过滤重复）")
    
    def test_update_basic(self):
        """测试基本更新"""
        print("\n" + "="*80)
        print("🚀 开始测试 Table 更新功能")
        print("="*80)
        
        print("\n✅ 测试11：基本更新")
        
        # 先查询一条数据
        data = self.table.query(name='测试用户1', limit=1)
        if data:
            user_id = data[0]['id']
            affect = self.table.update(new={'age': 29, 'job': '高级测试工程师'}, id=user_id)
            print(f"   更新 id={user_id}，影响行数：{affect}")
            
            # 验证更新
            updated = self.table.query(id=user_id)
            if updated:
                print(f"   验证更新：age={updated[0]['age']}, job={updated[0]['job']}")
    
    def test_update_one(self):
        """测试单条更新（update_one）"""
        print("\n✅ 测试12：update_one 方法")
        
        data = self.table.query(name='测试用户2', limit=1)
        if data:
            user = data[0]
            user['age'] = 26
            user['salary'] = 15000
            affect = self.table.update_one(user, depend='id')
            print(f"   使用 update_one 更新，影响行数：{affect}")
    
    def test_update_many(self):
        """测试批量更新（update_many）"""
        print("\n✅ 测试13：update_many 方法")
        
        # 准备批量更新数据
        users = self.table.query(pick='id, name, age', limit=3)
        if users:
            for user in users:
                user['age'] = user['age'] + 1
            
            affect = self.table.update_many(users, depend='id')
            print(f"   批量更新 {len(users)} 条，影响行数：{affect}")
    
    def test_update_some(self):
        """测试 update_some（一条SQL更新多条）"""
        print("\n✅ 测试14：update_some 方法（一条SQL）")
        
        users = self.table.query(pick='id, salary', limit=3)
        if users:
            for user in users:
                user['salary'] = (user.get('salary') or 0) + 1000
            
            affect = self.table.update_some(users, depend='id')
            print(f"   使用一条SQL更新 {len(users)} 条，影响行数：{affect}")
    
    def test_cvs(self):
        """测试 cvs（检查值存在性）"""
        print("\n✅ 测试15：cvs 方法（检查值存在性）")
        
        phones = ['13800138000', '13800138001', '19900000000', '19900000001']
        new_phones, old_phones = self.table.cvs('phone', phones)
        print(f"   检查 {len(phones)} 个手机号")
        print(f"   不存在的：{new_phones}")
        print(f"   已存在的：{old_phones}")
    
    def test_delete(self):
        """测试删除"""
        print("\n" + "="*80)
        print("🚀 开始测试 Table 删除功能")
        print("="*80)
        
        print("\n✅ 测试16：删除数据")
        
        # 删除测试数据
        affect1 = self.table.delete(id=99999)
        print(f"   删除 id=99999：影响行数 {affect1}")
        
        # 批量删除
        data = self.table.query(name='去重1')
        if data:
            ids = [d['id'] for d in data]
            affect2 = self.table.delete(id=ids)
            print(f"   批量删除 {len(ids)} 条：影响行数 {affect2}")
        
        # 条件删除（带 limit）
        affect3 = self.table.delete(age=100, limit=10)  # 删除不存在的数据
        print(f"   条件删除（age=100, limit=10）：影响行数 {affect3}")
    
    def test_scan(self):
        """测试扫描功能"""
        print("\n" + "="*80)
        print("🚀 开始测试 Table 扫描功能")
        print("="*80)
        
        print("\n✅ 测试17：scan 方法（遍历表）")
        
        # 自定义处理函数
        total_count = 0
        
        def counter(lines):
            nonlocal total_count
            total_count += len(lines)
        
        # 扫描前100条
        min_id = self.table.get_min('id')
        print(f"   扫描 ID 范围：{min_id} ~ {min_id + 100}")
        
        self.table.scan(
            sort_field='id',
            start=min_id,
            end=min_id + 100,
            once=20,  # 每批20条
            dealer=counter,
            log=False,  # 不输出日志
            max_query_times=3  # 最多查询3次
        )
        
        print(f"   扫描完成，共处理 {total_count} 条数据")
    
    def run_all(self):
        """运行所有测试"""
        # 查询测试
        self.test_query_count()
        self.test_query_basic()
        self.test_query_in()
        self.test_exists()
        self.test_random()
        self.test_get_min_max()
        
        # 插入测试
        self.test_insert_single()
        self.test_insert_batch()
        self.test_insert_with_conflict()
        self.test_dedup_insert()
        
        # 更新测试
        self.test_update_basic()
        self.test_update_one()
        self.test_update_many()
        self.test_update_some()
        self.test_cvs()
        
        # 删除测试
        self.test_delete()
        
        # 扫描测试
        self.test_scan()
        
        print("\n" + "="*80)
        print("✅ Table 类测试完成")
        print("="*80)


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("🎯 SQLMan V2 完整测试套件")
    print("="*80)
    print("\n⚠️  请确保：")
    print("   1. MySQL 服务已启动")
    print("   2. 已修改 TestConfig 中的连接信息")
    print("   3. 测试数据库已创建（test_sqlman）")
    print("\n" + "="*80)
    
    try:
        # 测试 MySQL 类
        mysql_tester = TestV2MySQL()
        table = mysql_tester.run_all()
        
        if table is None:
            print("\n❌ MySQL 测试失败，终止后续测试")
            return
        
        # 测试 Table 类
        table_tester = TestV2Table(table)
        table_tester.run_all()
        
        print("\n" + "="*80)
        print("🎉 所有测试完成！")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

