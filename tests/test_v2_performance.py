"""
SQLMan V2 性能测试
测试批量操作、大数据量场景的性能

运行方式：
    python -m sqlman.tests.test_v2_performance
    或
    cd sqlman/tests && python test_v2_performance.py
"""

import sys
import time
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


class PerformanceTest:
    """性能测试类"""
    
    def __init__(self, config):
        self.db = MySQL(**config)
        self.table_name = 'perf_test_table'
        self.table = None
    
    def setup(self):
        """初始化测试表"""
        print("\n🔧 初始化测试环境...")
        
        # 删除旧表
        if self.table_name in self.db.get_tables():
            self.db.remove_table(self.table_name)
        
        # 创建测试表（10000条数据）
        self.table = self.db.gen_test_table(self.table_name, once=1000, total=10000)
        print(f"✓ 测试表创建完成：{self.table_name}，包含 10000 条数据\n")
    
    def test_batch_insert(self):
        """测试批量插入性能"""
        print("="*70)
        print("📊 测试1：批量插入性能")
        print("="*70)
        
        # 准备数据
        batch_sizes = [10, 100, 500, 1000]
        
        for size in batch_sizes:
            data = [
                {'name': f'批量用户{i}', 'age': 20 + i % 40, 'gender': '男' if i % 2 == 0 else '女'}
                for i in range(size)
            ]
            
            start = time.time()
            affect = self.table.insert_data(data)
            elapsed = time.time() - start
            
            speed = size / elapsed if elapsed > 0 else 0
            print(f"  插入 {size:4d} 条：耗时 {elapsed:.3f}s，速度 {speed:.0f} 条/秒，影响 {affect} 行")
    
    def test_batch_update(self):
        """测试批量更新性能"""
        print("\n" + "="*70)
        print("📊 测试2：批量更新性能")
        print("="*70)
        
        batch_sizes = [10, 100, 500]
        
        for size in batch_sizes:
            # 获取数据
            data = self.table.query(pick='id, age', limit=size)
            if not data:
                continue
            
            # 修改数据
            for item in data:
                item['age'] = item['age'] + 1
            
            # update_many 方式（多条SQL）
            start = time.time()
            affect = self.table.update_many(data, depend='id')
            elapsed = time.time() - start
            speed = size / elapsed if elapsed > 0 else 0
            print(f"  update_many {size:3d} 条：耗时 {elapsed:.3f}s，速度 {speed:.0f} 条/秒")
            
            # update_some 方式（一条SQL）
            for item in data:
                item['age'] = item['age'] + 1
            
            start = time.time()
            affect = self.table.update_some(data, depend='id')
            elapsed = time.time() - start
            speed = size / elapsed if elapsed > 0 else 0
            print(f"  update_some {size:3d} 条：耗时 {elapsed:.3f}s，速度 {speed:.0f} 条/秒")
            print()
    
    def test_query_performance(self):
        """测试查询性能"""
        print("="*70)
        print("📊 测试3：查询性能")
        print("="*70)
        
        # 测试不同 limit 的查询性能
        limits = [10, 100, 500, 1000, 5000]
        
        for limit in limits:
            start = time.time()
            data = self.table.query(limit=limit)
            elapsed = time.time() - start
            
            speed = len(data) / elapsed if elapsed > 0 else 0
            print(f"  查询 {limit:4d} 条：耗时 {elapsed:.3f}s，速度 {speed:.0f} 条/秒，实际 {len(data)} 条")
    
    def test_scan_performance(self):
        """测试扫描性能"""
        print("\n" + "="*70)
        print("📊 测试4：scan 扫描性能")
        print("="*70)
        
        total_processed = 0
        
        def counter(lines):
            nonlocal total_processed
            total_processed += len(lines)
        
        min_id = self.table.get_min('id')
        max_id = self.table.get_max('id')
        
        start = time.time()
        self.table.scan(
            sort_field='id',
            start=min_id,
            end=max_id,
            once=1000,
            dealer=counter,
            log=False,
            rest=0  # 不休息
        )
        elapsed = time.time() - start
        
        speed = total_processed / elapsed if elapsed > 0 else 0
        print(f"  扫描全表：耗时 {elapsed:.3f}s，处理 {total_processed} 条，速度 {speed:.0f} 条/秒")
    
    def test_dedup_insert_performance(self):
        """测试去重插入性能"""
        print("\n" + "="*70)
        print("📊 测试5：去重插入性能")
        print("="*70)
        
        # 准备数据（50%是重复的）
        existing = self.table.query(pick='phone', limit=500)
        existing_phones = [d['phone'] for d in existing if d.get('phone')]
        
        test_data = []
        for i in range(1000):
            if i < 500 and i < len(existing_phones):
                # 使用已存在的 phone（重复数据）
                phone = existing_phones[i]
            else:
                # 新的 phone
                phone = f'1390000{i:04d}'
            
            test_data.append({
                'name': f'去重测试{i}',
                'phone': phone,
                'age': 25
            })
        
        start = time.time()
        affect = self.table.dedup_insert_data(test_data, dedup='phone')
        elapsed = time.time() - start
        
        print(f"  去重插入：总数 {len(test_data)} 条，实际插入 {affect} 条")
        print(f"  耗时：{elapsed:.3f}s，去重率：{(1 - affect/len(test_data))*100:.1f}%")
    
    def cleanup(self):
        """清理测试数据"""
        print("\n🧹 清理测试环境...")
        self.db.remove_table(self.table_name)
        print("✓ 清理完成")
    
    def run_all(self):
        """运行所有性能测试"""
        print("\n" + "="*70)
        print("🎯 SQLMan V2 性能测试")
        print("="*70)
        
        try:
            self.setup()
            self.test_batch_insert()
            self.test_batch_update()
            self.test_query_performance()
            self.test_scan_performance()
            self.test_dedup_insert_performance()
            
            print("\n" + "="*70)
            print("✅ 性能测试完成")
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
    
    tester = PerformanceTest(MYSQL_CONFIG)
    tester.run_all()


if __name__ == '__main__':
    main()

