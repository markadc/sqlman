# SQLMan

<p align="center">
    <em>告别 SQL 语句，让 Python 操作 MySQL 更优雅</em>
</p>

<p align="center">
    <a href="https://github.com/markadc/sqlman"><img src="https://img.shields.io/badge/version-0.4.6-blue.svg" alt="Version"></a>
    <a href="https://github.com/markadc/sqlman/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-orange.svg" alt="Python Version"></a>
</p>

---

## 📋 目录

- [特性](#-特性)
- [安装](#-安装)
- [快速开始](#-快速开始)
  - [连接数据库](#1-连接数据库)
  - [获取表对象](#2-获取表对象)
  - [生成测试数据](#3-生成测试数据)
- [核心功能](#-核心功能)
  - [插入数据](#插入数据)
  - [删除数据](#删除数据)
  - [更新数据](#更新数据)
  - [查询数据](#查询数据)
  - [随机数据](#随机数据)
  - [遍历表](#遍历表)
- [更新历史](#-更新历史)
- [依赖项](#-依赖项)
- [许可证](#-许可证)

---

## ✨ 特性

- 🚀 **零 SQL 编写** - 纯 Python 方法调用完成增删改查
- 🎯 **简洁优雅** - API 设计简单直观，上手即用
- 🔌 **连接便捷** - 支持字典配置、URL 连接等多种方式
- 💡 **智能推断** - 自动识别单条/批量插入，无需手动区分
- 🛡️ **冲突处理** - 内置多种数据冲突处理策略
- 🔄 **连接池管理** - 基于 DBUtils 的高效连接池
- 🎲 **实用工具** - 提供测试数据生成、随机采样等实用功能
- 📦 **生产就绪** - 持续更新，稳定可靠

---

## 📦 安装

```bash
pip install sqlman
```

**环境要求：** Python 3.10+

---

## 🚀 快速开始

### 1. 连接数据库

SQLMan 提供三种灵活的连接方式：

**方式一：直接传参**

```python
from sqlman import Connector

db = Connector(
    host="localhost",
    port=3306,
    username="root",
    password="your_password",
    db="test"
)
```

**方式二：字典配置**

```python
from sqlman import Connector

MYSQL_CONF = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': 'your_password',
    'db': 'test'
}
db = Connector(**MYSQL_CONF)
```

**方式三：URL 连接**

```python
from sqlman import Connector

MYSQL_URL = "mysql://root:your_password@localhost:3306/test"
db = Connector.from_url(MYSQL_URL)
```

### 2. 获取表对象

```python
# 方法1：使用索引方式
student = db['student']

# 方法2：使用 pick_table 方法
student = db.pick_table('student')
```

### 3. 生成测试数据

SQLMan 提供便捷的测试数据生成功能，一行代码创建表并填充数据：

```python
# 创建 people 表并插入测试数据
# once: 每批插入数量，total: 总共插入数量
people = db.gen_test_table('people', once=1000, total=10000)
```

---

## 🔧 核心功能

### 插入数据

SQLMan 智能识别数据类型，自动选择单条或批量插入，并提供多种冲突处理策略。

#### 单条插入

```python
data = {'id': 10001, 'name': '小明', 'age': 10, 'gender': '男'}

# 基本插入
people.insert_data(data)
```

#### 批量插入

```python
data = [
    {'id': 10002, 'name': '小红', 'age': 12, 'gender': '女'},
    {'id': 10003, 'name': '小强', 'age': 13, 'gender': '男'},
    {'id': 10004, 'name': '小白', 'age': 14, 'gender': '男'}
]

# 自动识别为批量插入
people.insert_data(data)
```

#### 冲突处理策略

**策略 1：忽略冲突**

```python
# 数据冲突时不报错，忽略冲突数据
people.insert_data(data, unique='id')
```

**策略 2：冲突时更新**

```python
data = {'id': 10001, 'name': '小明', 'age': 10, 'gender': '男'}

# 数据冲突时，执行更新操作（此处将 age 加 1）
people.insert_data(data, update='age=age+1')
```

### 删除数据

```python
# 单条删除：DELETE FROM people WHERE id=1
people.delete(id=1)

# 批量删除：DELETE FROM people WHERE id IN (1, 2, 3)
people.delete(id=[1, 2, 3])

# 限制删除：DELETE FROM people WHERE age=18 LIMIT 100
people.delete(age=18, limit=100)
```

### 更新数据

```python
# 单字段更新：UPDATE people SET name='tony', job='理发师' WHERE id=1
people.update(new={'name': 'tony', 'job': '理发师'}, id=1)

# 多条件更新：UPDATE people SET job='程序员' WHERE name='thomas' AND phone='18959176772'
people.update(new={'job': '程序员'}, name='thomas', phone='18959176772')
```

### 查询数据

```python
# 基本查询：SELECT * FROM people WHERE id=1
people.query(id=1)

# 指定字段：SELECT name, age FROM people WHERE id=2
people.query(pick='name, age', id=2)

# IN 查询：SELECT * FROM people WHERE age=18 AND gender IN ('男', '女')
people.query(age=18, gender=['男', '女'])

# 限制数量：SELECT name FROM people WHERE age=18 AND gender IN ('男', '女') LIMIT 5
people.query(pick='name', age=18, gender=['男', '女'], limit=5)
```

### 随机数据

```python
# 随机返回 1 条数据（返回 dict）
result = people.random()
print(result)

# 随机返回 5 条数据（返回 list）
results = people.random(limit=5)
print(results)
```

### 遍历表

```python
# 基本遍历：默认每批扫描 1000 条，打印数据
people.scan()

# 自定义处理函数
def show(lines):
    for idx, item in enumerate(lines, start=1):
        print(f'第{idx}条  {item}')

# 高级遍历：限制 ID 范围，每批 100 条，使用自定义处理函数
people.scan(sort_field='id', start=101, end=222, once=100, dealer=show)

# 附加条件：在 ID 范围基础上，额外限制 age=18
people.scan(sort_field='id', start=101, end=222, once=100, dealer=show, add_cond='age=18')
```

---

## 📝 更新历史

### v0.4.6 (当前版本)

- 优化核心功能
- 改进连接池管理
- 增强错误处理

### v2.x

- 重构核心架构
- 提供更简洁的 API
- 支持更多高级特性

---

## 📦 依赖项

- **DBUtils** - 数据库连接池管理
- **PyMySQL** - MySQL 数据库驱动
- **Faker** - 测试数据生成
- **loguru** - 日志记录

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**项目地址：** [https://github.com/markadc/sqlman](https://github.com/markadc/sqlman)

**作者：** WangTuo (markadc@126.com)

---

<p align="center">
    <em>如果这个项目对你有帮助，欢迎 ⭐ Star 支持一下！</em>
</p>
