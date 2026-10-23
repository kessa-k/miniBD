import os
import struct

TEXT_LEN = 60
CODES = {"INT": "i", "FLOAT": "d", "STRING": f"{TEXT_LEN}s"}
INT_MIN = -2**31
INT_MAX = 2**31 - 1


class Table:
    def __init__(self, name, fields, folder):
        self.name = name
        self.fields = fields
        self.file = os.path.join(folder, name + ".taib")
        pattern = "<?"
        for _, kind, _ in fields:
            pattern += CODES[kind]
        self.pattern = pattern
        self.row_size = struct.calcsize(pattern)
        self.names = [name for name, _, _ in fields]
        self.key = None
        for i, (_, _, is_key) in enumerate(fields):
            if is_key:
                self.key = i

    def pack(self, values):
        row = [True]
        for value, (name, kind, _) in zip(values, self.fields):
            value = convert(value, kind, name)
            if kind == "STRING":
                value = value.encode("utf-8")
                if len(value) > TEXT_LEN:
                    raise ValueError(f"{name}: строка длиннее {TEXT_LEN} байт")
            row.append(value)
        return struct.pack(self.pattern, *row)

    def insert(self, values):
        values = self.complete(values)
        if self.key is not None:
            key_name = self.names[self.key]
            key_value = values[self.key]
            if self.find(key_name, "=", key_value):
                raise ValueError(f"{key_name}={key_value} уже есть в {self.name}")
        with open(self.file, "ab") as f:
            f.write(self.pack(values))
        return values[self.key] if self.key is not None else None

    def find(self, column=None, op=None, value=None):
        found = []
        if not os.path.exists(self.file):
            return found
        if column is not None:
            index = self.column(column)
            value = convert(value, self.fields[index][1], column)
        with open(self.file, "rb") as f:
            offset = 0
            while True:
                raw = f.read(self.row_size)
                if len(raw) < self.row_size:
                    break
                alive, *values = struct.unpack(self.pattern, raw)
                row = [clean(v) for v in values]
                if alive and (column is None or compare(row[index], op, value)):
                    found.append((offset, row))
                offset += self.row_size
        return found

    def select(self, column=None, op=None, value=None):
        return [row for _, row in self.find(column, op, value)]

    def delete(self, column, op, value):
        found = self.find(column, op, value)
        if not found:
            return 0
        with open(self.file, "r+b") as f:
            for offset, _ in found:
                f.seek(offset)
                f.write(struct.pack("<?", False))
        return len(found)

    def update(self, set_column, new_value, column, op, value):
        i = self.column(set_column)
        if i == self.key:
            raise ValueError(f"первичный ключ {set_column} менять нельзя")
        found = self.find(column, op, value)
        if not found:
            return 0
        with open(self.file, "r+b") as f:
            for offset, row in found:
                row[i] = new_value
                f.seek(offset)
                f.write(self.pack(row))
        return len(found)

    def column(self, name):
        if name not in self.names:
            raise ValueError(f"в таблице {self.name} нет столбца {name}")
        return self.names.index(name)

    def next_id(self):
        ids = [row[self.key] for row in self.select()]
        if ids:
            return max(ids) + 1
        return 1

    def complete(self, values):
        if self.key is not None and len(values) == len(self.fields) - 1:
            values = values[:self.key] + [self.next_id()] + values[self.key:]
        if len(values) != len(self.fields):
            raise ValueError(
                f"нужно {len(self.fields)} значений "
                f"(или {len(self.fields) - 1} без id), а пришло {len(values)}"
            )
        return values

def clean(value):
    if isinstance(value, bytes):
        return value.rstrip(b"\x00").decode("utf-8")
    return value

def convert(value, kind,name=""):
    try:
        if kind == "INT":
            value = int(value)
            if not INT_MIN <= value <= INT_MAX:
                raise ValueError
            return value
        if kind == "FLOAT":
            return float(value)
    except ValueError:
        raise ValueError(f"{name}: значение {value} не подходит под тип {kind}")
    return value

def compare(a, op, b):
    if op == "=":
        return a == b
    if op == "!=":
        return a != b
    if op == ">":
        return a > b
    if op == "<":
        return a < b
    if op == ">=":
        return a >= b
    if op == "<=":
        return a <= b
    raise ValueError(f"неизвестный оператор {op}")