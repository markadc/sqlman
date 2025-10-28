"""
SQLMan V2 测试运行器
一键运行所有测试

运行方式：
    python -m sqlman.tests.run_all_tests
    或
    cd sqlman/tests && python run_all_tests.py
    
    # 或者指定运行某些测试
    python -m sqlman.tests.run_all_tests --quick
    python -m sqlman.tests.run_all_tests --complete
    python -m sqlman.tests.run_all_tests --performance
    python -m sqlman.tests.run_all_tests --edge-cases
"""

import sys
import time
import argparse
from pathlib import Path

# 支持直接运行
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = []
        self.total_time = 0
    
    def run_test(self, test_name, test_func):
        """运行单个测试"""
        print("\n" + "="*80)
        print(f"🚀 运行测试：{test_name}")
        print("="*80)
        
        start_time = time.time()
        
        try:
            test_func()
            elapsed = time.time() - start_time
            self.results.append({
                'name': test_name,
                'status': '✅ 通过',
                'time': elapsed
            })
            print(f"\n✅ {test_name} 完成，耗时 {elapsed:.2f}秒")
            return True
        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            self.results.append({
                'name': test_name,
                'status': '⚠️ 中断',
                'time': elapsed
            })
            print(f"\n⚠️ {test_name} 被用户中断")
            raise
        except Exception as e:
            elapsed = time.time() - start_time
            self.results.append({
                'name': test_name,
                'status': '❌ 失败',
                'time': elapsed,
                'error': str(e)
            })
            print(f"\n❌ {test_name} 失败，耗时 {elapsed:.2f}秒")
            print(f"错误：{e}")
            return False
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n\n" + "="*80)
        print("📊 测试摘要")
        print("="*80)
        
        for result in self.results:
            time_str = f"{result['time']:.2f}s"
            print(f"  {result['status']} {result['name']:<30} {time_str:>10}")
            if 'error' in result:
                print(f"       ↳ {result['error']}")
        
        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if '✅' in r['status'])
        failed = sum(1 for r in self.results if '❌' in r['status'])
        interrupted = sum(1 for r in self.results if '⚠️' in r['status'])
        total_time = sum(r['time'] for r in self.results)
        
        print("\n" + "-"*80)
        print(f"  总计：{total} 个测试")
        print(f"  通过：{passed} 个")
        print(f"  失败：{failed} 个")
        if interrupted > 0:
            print(f"  中断：{interrupted} 个")
        print(f"  总耗时：{total_time:.2f}秒")
        print("="*80)
        
        # 返回是否全部通过
        return failed == 0 and interrupted == 0


def run_quick_test():
    """运行快速测试"""
    try:
        from .test_v2_quick import quick_test
    except ImportError:
        from test_v2_quick import quick_test
    quick_test()


def run_complete_test():
    """运行完整测试"""
    try:
        from .test_v2_complete import TestV2MySQL, TestV2Table
    except ImportError:
        from test_v2_complete import TestV2MySQL, TestV2Table
    
    mysql_tester = TestV2MySQL()
    table = mysql_tester.run_all()
    
    if table:
        table_tester = TestV2Table(table)
        table_tester.run_all()


def run_performance_test():
    """运行性能测试"""
    try:
        from .test_v2_performance import PerformanceTest
    except ImportError:
        from test_v2_performance import PerformanceTest
    
    tester = PerformanceTest(MYSQL_CONFIG)
    tester.run_all()


def run_edge_cases_test():
    """运行边界测试"""
    try:
        from .test_v2_edge_cases import EdgeCaseTest
    except ImportError:
        from test_v2_edge_cases import EdgeCaseTest
    
    tester = EdgeCaseTest(MYSQL_CONFIG)
    tester.run_all()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SQLMan V2 测试运行器')
    parser.add_argument('--quick', action='store_true', help='只运行快速测试')
    parser.add_argument('--complete', action='store_true', help='只运行完整测试')
    parser.add_argument('--performance', action='store_true', help='只运行性能测试')
    parser.add_argument('--edge-cases', action='store_true', help='只运行边界测试')
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner()
    
    print("\n" + "="*80)
    print("🎯 SQLMan V2 测试套件")
    print("="*80)
    print(f"\n📊 数据库配置：{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['db']}")
    print("\n⚠️  运行前请确保：")
    print("   1. MySQL 服务已启动")
    print("   2. 已在 test_config.py 中配置数据库连接信息")
    print(f"   3. 测试数据库已创建（{MYSQL_CONFIG['db']}）")
    print("\n按 Ctrl+C 可随时中断测试")
    print("="*80)
    
    try:
        # 根据参数决定运行哪些测试
        if args.quick:
            runner.run_test("快速测试", run_quick_test)
        elif args.complete:
            runner.run_test("完整功能测试", run_complete_test)
        elif args.performance:
            runner.run_test("性能测试", run_performance_test)
        elif args.edge_cases:
            runner.run_test("边界情况测试", run_edge_cases_test)
        else:
            # 运行所有测试
            runner.run_test("1. 快速测试", run_quick_test)
            time.sleep(1)
            
            runner.run_test("2. 完整功能测试", run_complete_test)
            time.sleep(1)
            
            runner.run_test("3. 性能测试", run_performance_test)
            time.sleep(1)
            
            runner.run_test("4. 边界情况测试", run_edge_cases_test)
        
        # 打印摘要
        all_passed = runner.print_summary()
        
        if all_passed:
            print("\n🎉 所有测试通过！")
            sys.exit(0)
        else:
            print("\n⚠️  部分测试失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        runner.print_summary()
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 测试运行器出错：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

