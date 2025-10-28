"""
测试配置示例文件

使用方法：
1. 复制此文件为 test_config.py（已自动创建）
2. 修改 test_config.py 中的数据库连接信息
3. test_config.py 已被加入 .gitignore，不会被提交到 git

注意：
- 不要直接修改此文件（test_config_example.py）
- 修改 test_config.py 即可
"""

# MySQL 连接配置（字典方式）
MYSQL_CONFIG = {
    'host': 'localhost',         # 数据库地址
    'port': 3306,                # 端口
    'username': 'root',          # 用户名
    'password': 'your_password', # 密码（请修改）
    'db': 'test_sqlman'          # 数据库名
}

# MySQL 连接配置（URL 方式）
MYSQL_URL = "mysql://root:your_password@localhost:3306/test_sqlman"

# 测试表名前缀
TEST_TABLE_PREFIX = 'test_'

# 是否在测试后清理数据
AUTO_CLEANUP = True

# 是否显示详细日志
VERBOSE = True

