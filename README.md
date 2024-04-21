# 说明

- 持续更新中...
- 从此告别SQL语句，直接调用方法就完事
- python3.10+

# 如何吸引你？

### 如此简易的连接方式

一个字典参数即可

### 插入数据如此的贴心

自动推导

- 传入dict是插入一条数据，传入list是插入多条数据

插入模式

- 默认插入，数据冲突则报错
- 插入时，数据冲突则不报错
- 插入时，数据冲突则不报错，还可以同时更新数据
- 插入时，则提前过滤掉会冲突的数据，只插入不冲突的数据

### 等等等等...

# 具体演示

### 连接mysql

```python
from sqlman import Handler

# 用来连接test数据库
mysql_cfg = {
    'host': 'localhost',
    'port': 3306,
    'db': 'test',
    'user': 'admin',
    'passwd': 'admin@1',
}

# 数据库对象
handler = Handler(mysql_cfg)

# 表格对象
people = handler['people']  
```

### 准备测试数据

```python
# 一条龙服务，创建people表并插入测试数据，每次插入一千条，累计插入一万条
handler.make_datas('people', once=1000, total=10000)
```

### 插入数据

#### 单条插入

```python
data = {'id': 10001, 'name': '小明', 'age': 10, 'gender': '男'}

# 插入一条数据
people.insert_data(data)

# 当插入的数据与表中的数据存在冲突时，直接插入会报错，如果补充<unque_index>参数，则不报错
people.insert_data(data, unique_index='id')

```

#### 批量插入

```python
data = [
    {'id': 10002, 'name': '小红', 'age': 12, 'gender': '女'},
    {'id': 10003, 'name': '小强', 'age': 13, 'gender': '男'},
    {'id': 10004, 'name': '小白', 'age': 14, 'gender': '男'}
]

# 插入多条数据
people.insert_data(data)
```

#### 插入数据时，如果数据冲突则进行更新

```python
data = {'id': 10001, 'name': '小明', 'age': 10, 'gender': '男'}

# 当数据冲突时，也可以直接进行更新操作，下面是把age更新为11
people.insert_data(data, update='age=age+1')
```

### 删除数据

```python
# delete from people where id=1
people.delete(id=1)

# delete from people where id in (1, 2, 3)
people.delete(id=[1, 2, 3])

# delete from people where age=18 limit 100
people.delete(age=18, limit=100)
```

### 更新数据

```python
# update people set name='tony', job='理发师' where id=1
people.update(new={'name': 'tony', 'job': '理发师'}, id=1)

# update people set job='程序员' where name='thomas' and phone='18959176772'
people.update(new={'job': '程序员'}, name='thomas', phone='18959176772')
```

### 查询数据

```python
# select * from people where id=1
people.query(id=1)

# select name, age from people where id=2
people.query(pick='name, age', id=2)

# select * from people where age=18 and gender in ('男', '女')
people.query(age=18, gender=['男', '女'])

# select name from people where age=18 and gender in ('男', '女') limit 5
people.query(pick='name', age=18, gender=['男', '女'], limit=5)
```

### 随机数据

```python
# 随机返回1条数据<dict>
print(people.random())

# 随机返回5条数据<list>
print(people.random(limit=5))
```

### 遍历表

```python
def show(datas):
    for some in enumerate(datas, start=1):
        print('第{}条  {}'.format(*some))


# 遍历整张表，默认每轮扫描1000条，默认只打印数据
people.scan()

# 限制id范围为101~222，每轮扫描100条，每轮的回调函数为show
people.scan('people', sort_field='id', start=101, end=222, once=100, dealer=show)

# 限制id范围的基础上，限制age=18
people.scan('people', sort_field='id', start=101, end=222, once=100, dealer=show, add_cond='age=18')
```