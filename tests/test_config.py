"""
SQLMan 测试配置文件

修改这里的数据库配置，所有测试都会使用
"""

# MySQL 连接配置（字典方式）
MYSQL_CONFIG = {
    'host': 'localhost',         # 数据库地址
    'port': 3306,                # 端口
    'username': 'root',          # 用户名
    'password': 'admin0',        # 密码
    'db': 'test'                 # 数据库名
}

# MySQL 连接配置（URL 方式）
MYSQL_URL = f"mysql://{MYSQL_CONFIG['username']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['db']}"

# 测试表名前缀
TEST_TABLE_PREFIX = 'test_'

# 是否在测试后清理数据
AUTO_CLEANUP = True

# 是否显示详细日志
VERBOSE = True

