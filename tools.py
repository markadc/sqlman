def getfv(data: dict | list) -> tuple:
    item = data if isinstance(data, dict) else data[0]
    fs = []
    vs = []
    for k in item.keys():
        fs.append('`{}`'.format(k))
        vs.append('%s')
    fileds = ', '.join(fs)
    values = ', '.join(vs)
    return fileds, values


def make_result(**kwargs) -> dict:
    result = dict(**kwargs)
    return result


def make_set(data: dict):
    """SET ..."""
    fs = []
    args = []
    for k, v in data.items():
        fs.append('`{}`=%s'.format(k))
        args.append(v)
    _set = ', '.join(fs)
    return _set, args


# data = {'name': "CLOS", "age": 22}
# print("make_set\n{}\n{}\n".format(data, make_set(data)))


def make_in(some: list):
    """in ..."""
    _in = "({})".format(", ".join(["%s"] * len(some)))
    return _in, some


# some = "mark CLOS thomas claus charo".split()
# print("make_in\n{}\n{}\n".format(some, make_in(some)))


def make_where(data: dict):
    """WHERE ..."""
    if not data:
        return '', []
    conds = []
    args = []
    for k, v in data.items():
        if isinstance(v, list):
            _in, args1 = make_in(v)
            part = "`{}` in {}".format(k, _in)
            args += args1
        else:
            part = "`{}`=%s".format(k)
            args.append(v)
        conds.append(part)
    _where = " and ".join(conds)
    return _where, args


# data = dict(name="CLOS", age=[18, 22, 35, 60], vip=1)
# print("make_where\n{}\n{}\n".format(data, make_where(data)))

def make_tail(_where: str, _limit: int = None):
    where = "where {}".format(_where) if _where else ''
    limit = "limit {}".format(_limit) if _limit else ''
    tail = "{} {}".format(where, limit).strip()
    return tail


def red_print(s):
    """红色的打印"""
    print('\033[31m{}\033[0m'.format(s))


def print_lines(lines: list):
    """仅配合scan"""
    for line in lines:
        red_print(line)


def check_items(items: list, must_exist: str):
    """
    校验items\n
    如果item结构不一致，则抛出异常

    Args:
        items: [{}, {}, {}]
        must_exist: 必须存在的字段
    """
    fields = None
    for item in items:
        assert item
        if fields is None:
            fields = set(item)
            continue
        assert must_exist in fields
        assert fields == set(item)
