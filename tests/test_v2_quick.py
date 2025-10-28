"""
SQLMan V2 快速测试
用于快速验证核心功能是否正常

运行方式：
    python -m sqlman.tests.test_v2_quick
    或
    cd sqlman/tests && python test_v2_quick.py
"""

import sys
from pathlib import Path

# 支持直接运行
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlman.core.v2 import MySQL

# 导入统一配置
try:
    from .test_config import MYSQL_CONFIG as config
except ImportError:
    try:
        from test_config import MYSQL_CONFIG as config
    except ImportError:
        print("⚠️  未找到 test_config.py，请先创建配置文件")
        print("   可以复制 test_config_example.py 为 test_config.py 并修改配置")
        sys.exit(1)


def quick_test():
    """快速测试核心功能"""
    
    print("="*60)
    print("🚀 SQLMan V2 快速测试")
    print("="*60)
    print(f"📊 数据库：{config['host']}:{config['port']}/{config['db']}")
    print("="*60)
    
    try:
        # 1. 连接数据库
        print("\n1️⃣  连接数据库...")
        db = MySQL(**config)
        print("   ✓ 连接成功")
        
        # 2. 获取表列表
        print("\n2️⃣  获取表列表...")
        tables = db.get_tables()
        print(f"   ✓ 当前有 {len(tables)} 张表")
        
        # 3. 创建测试表
        print("\n3️⃣  创建测试表...")
        test_table = 'quick_test_table'
        if test_table in tables:
            db.remove_table(test_table)
        
        table = db.gen_test_table(test_table, once=50, total=100)
        print(f"   ✓ 表 '{test_table}' 创建成功，插入 100 条数据")
        
        # 4. 查询数据
        print("\n4️⃣  查询数据...")
        count = table.query_count()
        data = table.query(limit=3)
        print(f"   ✓ 总数：{count}，查询前3条：{len(data)} 条")
        
        # 5. 插入数据
        print("\n5️⃣  插入数据...")
        new_data = {'name': '快速测试', 'age': 25, 'gender': '男'}
        affect = table.insert_data(new_data)
        print(f"   ✓ 插入成功，影响 {affect} 行")
        
        # 6. 更新数据
        print("\n6️⃣  更新数据...")
        result = table.query(name='快速测试', limit=1)
        if result:
            user_id = result[0]['id']
            affect = table.update(new={'age': 26}, id=user_id)
            print(f"   ✓ 更新成功，影响 {affect} 行")
        
        # 7. 删除数据
        print("\n7️⃣  删除数据...")
        if result:
            affect = table.delete(id=user_id)
            print(f"   ✓ 删除成功，影响 {affect} 行")
        
        # 8. 清理测试表
        print("\n8️⃣  清理测试表...")
        db.remove_table(test_table)
        print("   ✓ 清理完成")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    quick_test()

