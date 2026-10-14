import os
import struct

TEXT_LEN = 60
CODES = {"INT": "i", "FLOAT": "d", "STRING": f"{TEXT_LEN}s"}


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

    def pack(self, values):
        row = [True]
        for value, (_, kind, _) in zip(values, self.fields):
            value = convert(value, kind)
            if kind == "STRING":
                value = value.encode("utf-8")
            row.append(value)
        return struct.pack(self.pattern, *row)

    def insert(self, values):
        with open(self.file, "ab") as f:
            f.write(struct.pack(self.pattern, *row))

    def find(self, column=None, op=None, value=None):
        found = []
        if not os.path.exists(self.file):
            return found
        if column is not None:
            names = [name for name, _, _ in self.fields]
            index = names.index(column)
            value = convert(value, self.fields[index][1])
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
        found = self.find(column, op, value)
        if not found:
            return 0
        names = [name for name, _, _ in self.fields]
        i = names.index(set_column)
        with open(self.file, "r+b") as f:
            for offset, row in found:
                row[i] = new_value
                f.seek(offset)
                f.write(self.pack(row))
        return len(found)

def clean(value):
    if isinstance(value, bytes):
        return value.rstrip(b"\x00").decode("utf-8")
    return value

def convert(value, kind):
    if kind == "INT":
        return int(value)
    if kind == "FLOAT":
        return float(value)
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