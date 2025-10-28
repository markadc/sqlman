# SQLMan 测试文档

欢迎使用 SQLMan 测试套件！本目录包含完整的 v2 API 测试代码。

## 📁 文件说明

| 文件                     | 说明                   | 测试数量  | 运行时间 |
| ------------------------ | ---------------------- | --------- | -------- |
| `test_v2_quick.py`       | 快速测试，验证核心功能 | 8 个步骤  | ~0.2 秒  |
| `test_v2_complete.py`    | 完整功能测试           | 17 个用例 | ~0.3 秒  |
| `test_v2_performance.py` | 性能测试               | 5 个场景  | ~1.7 秒  |
| `test_v2_edge_cases.py`  | 边界情况测试           | 11 个场景 | ~0.1 秒  |
| `run_all_tests.py`       | 测试运行器             | 所有测试  | ~2.3 秒  |
| `test_config.py`         | 数据库配置文件         | -         | -        |

## 🚀 快速开始

### 1. 配置数据库

编辑 `test_config.py` 文件，修改为你的数据库配置：

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': 'admin0',  # 修改为你的密码
    'db': 'test'           # 修改为你的数据库
}
```

### 2. 创建测试数据库

```sql
CREATE DATABASE test DEFAULT CHARSET=utf8mb4;
```

### 3. 运行测试

**快速验证（推荐）：**

```bash
python -m sqlman.tests.test_v2_quick
```

**运行所有测试：**

```bash
python -m sqlman.tests.run_all_tests
```

## 📋 详细测试说明

### test_v2_quick.py - 快速测试

**用途：** 快速验证环境配置和核心功能

**测试内容：**

1. 连接数据库
2. 获取表列表
3. 创建测试表
4. 查询数据
5. 插入数据
6. 更新数据
7. 删除数据
8. 清理测试表

**运行方式：**

```bash
# 方式1：模块运行
python -m sqlman.tests.test_v2_quick

# 方式2：直接运行
cd sqlman/tests
python test_v2_quick.py
```

### test_v2_complete.py - 完整功能测试

**用途：** 全面测试所有 API 功能

**测试分类：**

#### MySQL 类测试（5 个）

- 字典配置连接
- URL 连接方式
- 获取表列表
- 创建测试表
- 获取表对象

#### Table 类测试（12 个）

- **查询功能**：基本查询、IN 查询、条件查询、随机查询、存在性检查、最小/最大值
- **插入功能**：单条插入、批量插入、冲突处理、去重插入
- **更新功能**：基本更新、update_one、update_many、update_some、cvs 值检查
- **删除功能**：单条删除、批量删除、条件删除
- **高级功能**：scan 扫描遍历

**运行方式：**

```bash
python -m sqlman.tests.test_v2_complete
```

### test_v2_performance.py - 性能测试

**用途：** 评估大数据量场景下的性能表现

**测试场景：**

1. **批量插入性能** - 测试 10/100/500/1000 条数据的插入速度
2. **批量更新性能** - 对比 `update_many` vs `update_some` 的性能差异
3. **查询性能** - 测试不同 limit 值的查询速度
4. **scan 扫描性能** - 测试全表扫描的效率
5. **去重插入性能** - 测试 `dedup_insert_data` 的性能

**输出示例：**

```
插入  100 条：耗时 0.002s，速度 57440 条/秒
插入  500 条：耗时 0.004s，速度 130032 条/秒
插入 1000 条：耗时 0.006s，速度 168982 条/秒
```

**运行方式：**

```bash
python -m sqlman.tests.test_v2_performance
```

### test_v2_edge_cases.py - 边界情况测试

**用途：** 确保代码在异常情况下的健壮性

**测试场景：**

1. 空查询结果
2. 特殊字符（单引号、中文、emoji）
3. NULL 值处理
4. 空列表操作
5. 大数字处理
6. 长字符串处理
7. 更新不存在的数据
8. 删除不存在的数据
9. 特殊字段名查询
10. 多个复杂查询条件
11. cvs 方法边界情况

**运行方式：**

```bash
python -m sqlman.tests.test_v2_edge_cases
```

### run_all_tests.py - 测试运行器

**用途：** 一键运行所有测试，提供测试摘要

**功能：**

- 按顺序运行所有测试
- 统计测试结果（通过/失败/耗时）
- 显示详细的错误信息
- 支持选择性运行测试

**运行方式：**

```bash
# 运行所有测试
python -m sqlman.tests.run_all_tests

# 只运行快速测试
python -m sqlman.tests.run_all_tests --quick

# 只运行完整测试
python -m sqlman.tests.run_all_tests --complete

# 只运行性能测试
python -m sqlman.tests.run_all_tests --performance

# 只运行边界测试
python -m sqlman.tests.run_all_tests --edge-cases
```

**输出示例：**

```
================================================================================
📊 测试摘要
================================================================================
  ✅ 通过 1. 快速测试                             0.20s
  ✅ 通过 2. 完整功能测试                           0.24s
  ✅ 通过 3. 性能测试                             1.67s
  ✅ 通过 4. 边界情况测试                           0.10s
--------------------------------------------------------------------------------
  总计：4 个测试
  通过：4 个
  失败：0 个
  总耗时：2.21秒
================================================================================
🎉 所有测试通过！
```

## 🔧 测试覆盖率

### MySQL 类覆盖情况

| 方法             | 测试状态 | 说明             |
| ---------------- | -------- | ---------------- |
| `__init__`       | ✅       | 数据库连接初始化 |
| `from_url`       | ✅       | URL 连接方式     |
| `__getitem__`    | ✅       | 索引方式获取表   |
| `pick_table`     | ✅       | 方法方式获取表   |
| `exe_sql`        | ✅       | 执行 SQL         |
| `exem_sql`       | ✅       | 批量执行 SQL     |
| `get_tables`     | ✅       | 获取表列表       |
| `remove_table`   | ✅       | 删除表           |
| `gen_test_table` | ✅       | 生成测试表       |

**覆盖率：9/9 = 100%** ✅

### Table 类覆盖情况

| 方法                | 测试状态 | 说明                  |
| ------------------- | -------- | --------------------- |
| `insert_data`       | ✅       | 插入数据（单条/批量） |
| `dedup_insert_data` | ✅       | 去重插入              |
| `delete`            | ✅       | 删除数据              |
| `update`            | ✅       | 基本更新              |
| `update_one`        | ✅       | 单条更新              |
| `update_many`       | ✅       | 批量更新（多条 SQL）  |
| `update_some`       | ✅       | 批量更新（一条 SQL）  |
| `query`             | ✅       | 查询数据              |
| `query_count`       | ✅       | 查询数量              |
| `exists`            | ✅       | 检查存在性            |
| `random`            | ✅       | 随机查询              |
| `get_min`           | ✅       | 获取最小值            |
| `get_max`           | ✅       | 获取最大值            |
| `scan`              | ✅       | 扫描遍历              |
| `cvs`               | ✅       | 检查值存在性          |
| `remove`            | ✅       | 删除表                |

**覆盖率：16/16 = 100%** ✅

## 💡 自定义测试

你可以基于现有测试创建自己的测试：

```python
import sys
from pathlib import Path

# 支持直接运行
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlman.core import MySQL

# 导入配置
try:
    from .test_config import MYSQL_CONFIG
except ImportError:
    from test_config import MYSQL_CONFIG

# 连接数据库
db = MySQL(**MYSQL_CONFIG)

# 创建测试表
table = db.gen_test_table('my_test', once=100, total=500)

# 执行你的测试
result = table.query(limit=10)
print(f"查询结果：{len(result)} 条")

# 清理
db.remove_table('my_test')
```

## ⚙️ CI/CD 集成

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: test
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install -e .

      - name: Create test config
        run: |
          cat > sqlman/tests/test_config.py << EOF
          MYSQL_CONFIG = {
              'host': '127.0.0.1',
              'port': 3306,
              'username': 'root',
              'password': 'test_password',
              'db': 'test'
          }
          EOF

      - name: Run tests
        run: |
          python -m sqlman.tests.run_all_tests
```

## 🐛 常见问题

### Q1: 连接失败

```
❌ 连接失败：(2003, "Can't connect to MySQL server...")
```

**解决方案：**

- 检查 MySQL 服务是否启动
- 确认 `test_config.py` 中的连接信息是否正确
- 检查防火墙设置

### Q2: 表已存在

```
❌ 表格创建失败
```

**解决方案：**

- 手动删除测试表：`DROP TABLE IF EXISTS test_users;`
- 或者修改测试表名

### Q3: 权限不足

```
❌ (1142, "INSERT command denied...")
```

**解决方案：**

```sql
GRANT ALL PRIVILEGES ON test.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Q4: 找不到模块

```
ModuleNotFoundError: No module named 'sqlman'
```

**解决方案：**

```bash
# 方式1：安装包
pip install -e .

# 方式2：从 tests 目录直接运行
cd sqlman/tests
python test_v2_quick.py
```

## 📊 性能基准

基于 MySQL 8.0，本地测试环境：

| 操作           | 数据量   | 平均耗时 | 速度           |
| -------------- | -------- | -------- | -------------- |
| 批量插入       | 1000 条  | ~0.006s  | ~168,000 条/秒 |
| 批量更新(many) | 500 条   | ~0.042s  | ~12,000 条/秒  |
| 批量更新(some) | 500 条   | ~0.005s  | ~95,000 条/秒  |
| 查询           | 5000 条  | ~0.031s  | ~160,000 条/秒 |
| 扫描全表       | 11610 条 | ~0.081s  | ~143,000 条/秒 |

> 注：实际性能受网络、硬件、数据库配置等因素影响

## 🔒 注意事项

1. **使用测试数据库**：不要在生产数据库上运行测试
2. **自动清理**：测试会自动清理创建的表，无需手动操作
3. **并发测试**：避免同时运行多个测试，可能导致表名冲突

## 📚 相关文档

- [项目主 README](../../README.md)
- [sqlman 包 README](../README.md)
- [源码：db.py](../core/v2/db.py)
- [源码：table.py](../core/v2/table.py)

## 🤝 贡献测试

欢迎贡献新的测试用例！请确保：

1. 测试代码清晰易懂
2. 包含必要的注释
3. 能够独立运行
4. 自动清理测试数据
5. 遵循现有的测试风格

---

**作者：** WangTuo  
**项目：** [https://github.com/markadc/sqlman](https://github.com/markadc/sqlman)
