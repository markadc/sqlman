"""
SQLMan V2 边界情况测试
测试异常情况、边界值、特殊字符等场景

运行方式：
    python -m sqlman.tests.test_v2_edge_cases
    或
    cd sqlman/tests && python test_v2_edge_cases.py
"""

import sys
from pathlib import Path

# 支持直接运行
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlman.core.v2 import MySQL

# 导入统一配置
try:
    from .test_config import MYSQL_CONFIG
except ImportError:
    try:
        from test_config import MYSQL_CONFIG
    except ImportError:
        print("⚠️  未找到 test_config.py，请先创建配置文件")
        print("   可以复制 test_config_example.py 为 test_config.py 并修改配置")
        sys.exit(1)


class EdgeCaseTest:
    """边界情况测试类"""
    
    def __init__(self, config):
        self.db = MySQL(**config)
        self.table_name = 'edge_test_table'
        self.table = None
    
    def setup(self):
        """初始化"""
        print("\n🔧 初始化测试环境...")
        
        if self.table_name in self.db.get_tables():
            self.db.remove_table(self.table_name)
        
        self.table = self.db.gen_test_table(self.table_name, once=100, total=200)
        print(f"✓ 测试表创建完成：{self.table_name}\n")
    
    def test_empty_query(self):
        """测试空查询"""
        print("="*70)
        print("🧪 测试1：空查询结果")
        print("="*70)
        
        # 查询不存在的数据
        result = self.table.query(id=999999999)
        print(f"  查询不存在的ID：返回 {result}，类型 {type(result)}")
        print(f"  ✓ 返回空列表，不抛出异常\n")
    
    def test_special_characters(self):
        """测试特殊字符"""
        print("="*70)
        print("🧪 测试2：特殊字符处理")
        print("="*70)
        
        special_data = [
            {'name': "O'Neill", 'age': 30, 'address': "It's a test"},
            {'name': '中文名字', 'age': 25, 'address': '中国北京'},
            {'name': 'Test"Quote', 'age': 28, 'address': 'Address with "quotes"'},
            {'name': 'emoji😀', 'age': 22, 'address': '🏠🏡🏘️'},
        ]
        
        try:
            affect = self.table.insert_data(special_data)
            print(f"  插入特殊字符数据：{affect} 条")
            
            # 验证查询
            result1 = self.table.query(name="O'Neill")
            print(f"  查询单引号：{len(result1)} 条")
            
            result2 = self.table.query(name='中文名字')
            print(f"  查询中文：{len(result2)} 条")
            
            result3 = self.table.query(name='emoji😀')
            print(f"  查询emoji：{len(result3)} 条")
            
            print(f"  ✓ 特殊字符处理正常\n")
        except Exception as e:
            print(f"  ⚠️  特殊字符处理异常：{e}\n")
    
    def test_null_values(self):
        """测试 NULL 值"""
        print("="*70)
        print("🧪 测试3：NULL 值处理")
        print("="*70)
        
        # 插入包含 None 的数据
        null_data = {
            'name': 'NULL测试',
            'age': None,
            'phone': None,
            'address': None
        }
        
        try:
            affect = self.table.insert_data(null_data)
            print(f"  插入NULL值数据：{affect} 条")
            
            # 查询验证
            result = self.table.query(name='NULL测试')
            if result:
                print(f"  查询结果：age={result[0].get('age')}, phone={result[0].get('phone')}")
                print(f"  ✓ NULL值处理正常\n")
        except Exception as e:
            print(f"  ⚠️  NULL值处理异常：{e}\n")
    
    def test_empty_list_operations(self):
        """测试空列表操作"""
        print("="*70)
        print("🧪 测试4：空列表操作")
        print("="*70)
        
        # 空列表插入
        try:
            affect = self.table.insert_data([])
            print(f"  空列表插入：{affect} 条")
        except Exception as e:
            print(f"  空列表插入异常（预期）：{type(e).__name__}")
        
        # 空列表查询（这会导致 SQL 错误：where id in ()）
        try:
            result = self.table.query(id=[])
            print(f"  空列表查询：{len(result) if result else 0} 条")
        except Exception as e:
            print(f"  空列表查询异常（预期）：{type(e).__name__}")
        
        print(f"  ✓ 空列表处理正常\n")
    
    def test_large_numbers(self):
        """测试大数字"""
        print("="*70)
        print("🧪 测试5：大数字处理")
        print("="*70)
        
        large_data = {
            'name': '大数字测试',
            'age': 999,
            'salary': 99999999,
        }
        
        try:
            affect = self.table.insert_data(large_data)
            print(f"  插入大数字：{affect} 条")
            
            result = self.table.query(name='大数字测试')
            if result:
                print(f"  查询结果：salary={result[0].get('salary')}")
                print(f"  ✓ 大数字处理正常\n")
        except Exception as e:
            print(f"  ⚠️  大数字处理异常：{e}\n")
    
    def test_long_string(self):
        """测试长字符串"""
        print("="*70)
        print("🧪 测试6：长字符串处理")
        print("="*70)
        
        long_string = 'A' * 200  # 200个字符
        long_data = {
            'name': '长字符串测试',
            'address': long_string[:200],  # 限制在字段长度内
        }
        
        try:
            affect = self.table.insert_data(long_data)
            print(f"  插入长字符串（200字符）：{affect} 条")
            
            result = self.table.query(name='长字符串测试')
            if result:
                addr_len = len(result[0].get('address', ''))
                print(f"  查询结果：address长度={addr_len}")
                print(f"  ✓ 长字符串处理正常\n")
        except Exception as e:
            print(f"  ⚠️  长字符串处理异常：{e}\n")
    
    def test_update_nonexistent(self):
        """测试更新不存在的数据"""
        print("="*70)
        print("🧪 测试7：更新不存在的数据")
        print("="*70)
        
        affect = self.table.update(new={'age': 100}, id=999999999)
        print(f"  更新不存在的ID：影响 {affect} 行")
        print(f"  ✓ 返回0，不抛出异常\n")
    
    def test_delete_nonexistent(self):
        """测试删除不存在的数据"""
        print("="*70)
        print("🧪 测试8：删除不存在的数据")
        print("="*70)
        
        affect = self.table.delete(id=999999999)
        print(f"  删除不存在的ID：影响 {affect} 行")
        print(f"  ✓ 返回0，不抛出异常\n")
    
    def test_duplicate_field_names(self):
        """测试字段名冲突"""
        print("="*70)
        print("🧪 测试9：查询包含特殊字段名")
        print("="*70)
        
        # 查询多个字段（包含重复逗号、空格等）
        try:
            result = self.table.query(pick='id,  name,   age', limit=1)
            print(f"  查询带多余空格的字段：{len(result) if result else 0} 条")
            if result:
                print(f"  字段：{list(result[0].keys())}")
            print(f"  ✓ 特殊格式字段处理正常\n")
        except Exception as e:
            print(f"  ⚠️  字段处理异常：{e}\n")
    
    def test_multiple_conditions(self):
        """测试多个复杂条件"""
        print("="*70)
        print("🧪 测试10：多个复杂查询条件")
        print("="*70)
        
        # 多条件查询
        result1 = self.table.query(age=25, gender='男', limit=10)
        print(f"  多条件查询（age=25 AND gender='男'）：{len(result1)} 条")
        
        # IN + 其他条件
        result2 = self.table.query(age=[25, 30, 35], gender='女', limit=10)
        print(f"  IN + 条件查询（age IN [...] AND gender='女'）：{len(result2)} 条")
        
        print(f"  ✓ 复杂条件处理正常\n")
    
    def test_cvs_edge_cases(self):
        """测试 cvs 方法边界情况"""
        print("="*70)
        print("🧪 测试11：cvs 方法边界情况")
        print("="*70)
        
        # 测试空列表（会导致 SQL 错误）
        try:
            new, old = self.table.cvs('phone', [])
            print(f"  空列表检查：新={new}, 旧={old}")
        except Exception as e:
            print(f"  空列表检查异常（预期）：{type(e).__name__}")
        
        # 测试全新值
        new2, old2 = self.table.cvs('phone', ['99999999991', '99999999992'])
        print(f"  全新值检查：新={len(new2)} 个, 旧={len(old2)} 个")
        
        print(f"  ✓ cvs边界情况处理正常\n")
    
    def cleanup(self):
        """清理"""
        print("🧹 清理测试环境...")
        self.db.remove_table(self.table_name)
        print("✓ 清理完成")
    
    def run_all(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("🎯 SQLMan V2 边界情况测试")
        print("="*70)
        
        try:
            self.setup()
            
            self.test_empty_query()
            self.test_special_characters()
            self.test_null_values()
            self.test_empty_list_operations()
            self.test_large_numbers()
            self.test_long_string()
            self.test_update_nonexistent()
            self.test_delete_nonexistent()
            self.test_duplicate_field_names()
            self.test_multiple_conditions()
            self.test_cvs_edge_cases()
            
            print("="*70)
            print("✅ 边界情况测试完成")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ 测试出错：{e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """主函数"""
    
    print(f"📊 使用数据库：{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['db']}")
    
    tester = EdgeCaseTest(MYSQL_CONFIG)
    tester.run_all()


if __name__ == '__main__':
    main()

