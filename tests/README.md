# SQLMan V2 测试文档

这个目录包含了 SQLMan V2 版本的完整测试套件。

## 📁 测试文件说明

### 1. `test_v2_complete.py` - 完整功能测试

**最全面的测试套件**，涵盖所有核心功能：

- ✅ MySQL 类测试

  - 数据库连接（字典、URL 方式）
  - 获取表列表
  - 创建/删除测试表
  - 获取表对象

- ✅ Table 类测试
  - **查询功能**：基本查询、IN 查询、条件查询、随机查询
  - **插入功能**：单条插入、批量插入、冲突处理、去重插入
  - **更新功能**：基本更新、update_one、update_many、update_some
  - **删除功能**：单条删除、批量删除、条件删除
  - **高级功能**：scan 扫描、exists 检查、cvs 值检查、min/max 获取

**运行方式：**

```bash
python -m sqlman.tests.test_v2_complete.py
```

### 2. `test_v2_quick.py` - 快速测试

**轻量级测试**，快速验证核心功能是否正常：

- 连接数据库
- 创建测试表
- 基本增删改查
- 清理测试数据

**适用场景：**

- 快速验证环境配置
- 开发过程中的冒烟测试
- CI/CD 快速检查

**运行方式：**

```bash
python -m sqlman.tests.test_v2_quick.py
```

### 3. `test_v2_performance.py` - 性能测试

**压力测试**，评估大数据量场景下的性能：

- 批量插入性能（10/100/500/1000 条）
- 批量更新性能（update_many vs update_some）
- 查询性能（不同 limit 值）
- scan 扫描全表性能
- 去重插入性能

**运行方式：**

```bash
python -m sqlman.tests.test_v2_performance.py
```

**输出示例：**

```
插入  100 条：耗时 0.123s，速度 813 条/秒
插入  500 条：耗时 0.456s，速度 1096 条/秒
插入 1000 条：耗时 0.789s，速度 1268 条/秒
```

### 4. `test_v2_edge_cases.py` - 边界情况测试

**异常场景测试**，确保程序健壮性：

- 空查询结果处理
- 特殊字符（单引号、中文、emoji）
- NULL 值处理
- 空列表操作
- 大数字、长字符串
- 不存在数据的操作
- 复杂查询条件

**运行方式：**

```bash
python -m sqlman.tests.test_v2_edge_cases.py
```

### 5. `test_config_example.py` - 配置示例

测试配置文件模板，包含数据库连接等配置。

## 🚀 快速开始

### 1. 准备环境

**安装依赖：**

```bash
pip install DBUtils PyMySQL Faker loguru
```

**或者安装 sqlman：**

```bash
pip install sqlman
```

### 2. 配置数据库 ⭐

**创建测试数据库：**

```sql
CREATE DATABASE test DEFAULT CHARSET=utf8mb4;
```

**修改配置（只需修改一次！）：**

打开 `sqlman/tests/test_config.py` 文件，修改数据库连接信息：

```python
# MySQL 连接配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': 'your_password',  # ← 修改这里
    'db': 'test'                  # ← 修改这里
}
```

**✅ 完成！所有测试文件都会使用这个配置，无需在每个文件中重复配置。**

> 💡 提示：
>
> - `test_config.py` 是实际使用的配置文件
> - `test_config_example.py` 是配置模板，不要修改
> - `test_config.py` 已被加入 `.gitignore`，不会被提交到 git

### 3. 运行测试

**运行单个测试：**

```bash
# 快速测试
python -m sqlman.tests.test_v2_quick.py

# 完整测试
python -m sqlman.tests.test_v2_complete.py

# 性能测试
python -m sqlman.tests.test_v2_performance.py

# 边界测试
python -m sqlman.tests.test_v2_edge_cases.py
```

**运行所有测试：**

```bash
cd sqlman/tests
python test_v2_quick.py && \
python test_v2_complete.py && \
python test_v2_performance.py && \
python test_v2_edge_cases.py
```

## 📊 测试覆盖率

### MySQL 类（db.py）

- ✅ `__init__` - 数据库连接初始化
- ✅ `from_url` - URL 连接方式
- ✅ `__getitem__` - 索引方式获取表
- ✅ `pick_table` - 方法方式获取表
- ✅ `exe_sql` - 执行 SQL
- ✅ `exem_sql` - 批量执行 SQL
- ✅ `get_tables` - 获取表列表
- ✅ `remove_table` - 删除表
- ✅ `gen_test_table` - 生成测试表

### Table 类（table.py）

- ✅ `insert_data` - 插入数据（单条/批量）
- ✅ `dedup_insert_data` - 去重插入
- ✅ `delete` - 删除数据
- ✅ `update` - 基本更新
- ✅ `update_one` - 单条更新
- ✅ `update_many` - 批量更新（多条 SQL）
- ✅ `update_some` - 批量更新（一条 SQL）
- ✅ `query` - 查询数据
- ✅ `query_count` - 查询数量
- ✅ `exists` - 检查存在性
- ✅ `random` - 随机查询
- ✅ `get_min` - 获取最小值
- ✅ `get_max` - 获取最大值
- ✅ `scan` - 扫描遍历
- ✅ `cvs` - 检查值存在性
- ✅ `remove` - 删除表

## 🎯 测试策略建议

### 开发阶段

1. **功能开发后**：运行 `test_v2_quick.py` 快速验证
2. **提交代码前**：运行 `test_v2_complete.py` 全面测试
3. **性能优化**：运行 `test_v2_performance.py` 对比性能

### 上线前

1. 运行所有测试
2. 检查性能指标
3. 验证边界情况

### CI/CD 集成

```yaml
# GitHub Actions 示例
- name: Run Tests
  run: |
    python -m sqlman.tests.test_v2_quick.py
    python -m sqlman.tests.test_v2_complete.py
```

## 📝 自定义测试

### 创建自己的测试

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlman.core.v2 import MySQL

# 连接数据库
db = MySQL(
    host='localhost',
    port=3306,
    username='root',
    password='your_password',
    db='test_sqlman'
)

# 创建测试表
table = db.gen_test_table('my_test', once=100, total=500)

# 执行你的测试
result = table.query(limit=10)
print(f"查询结果：{len(result)} 条")

# 清理
db.remove_table('my_test')
```

## ⚠️ 注意事项

1. **测试数据库**：请使用专门的测试数据库，不要用生产数据库
2. **数据清理**：测试会自动清理创建的测试表
3. **并发测试**：避免同时运行多个测试，可能导致表名冲突
4. **网络延迟**：性能测试结果会受网络影响，建议本地测试

## 🐛 常见问题

### Q1: 连接失败

```
❌ 连接失败：(2003, "Can't connect to MySQL server...")
```

**解决方案：**

- 检查 MySQL 服务是否启动
- 确认连接信息是否正确
- 检查防火墙设置

### Q2: 表已存在

```
❌ 表格创建失败
```

**解决方案：**

- 手动删除测试表
- 或者修改测试表名

### Q3: 权限不足

```
❌ (1142, "INSERT command denied...")
```

**解决方案：**

- 确保数据库用户有足够权限
- 授予权限：`GRANT ALL PRIVILEGES ON test_sqlman.* TO 'root'@'localhost';`

## 📚 相关文档

- [项目 README](../README.md)
- [sqlman 文档](../sqlman/README.md)
- [源码：db.py](../sqlman/core/v2/db.py)
- [源码：table.py](../sqlman/core/v2/table.py)

## 🤝 贡献测试用例

欢迎提交新的测试用例！请确保：

1. 测试代码清晰易懂
2. 包含必要的注释
3. 能够独立运行
4. 自动清理测试数据

---

**作者：** WangTuo  
**项目：** [https://github.com/markadc/sqlman](https://github.com/markadc/sqlman)
