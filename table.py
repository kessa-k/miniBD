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

    def insert(self, values):
        row = [True]
        for value, (_, kind, _) in zip(values, self.fields):
            value = convert(value, kind)
            if kind == "STRING":
                value = value.encode("utf-8")
            row.append(value)
        with open(self.file, "ab") as f:
            f.write(struct.pack(self.pattern, *row))

    def select(self, column=None, op=None, value=None):
        rows = []
        if not os.path.exists(self.file):
            return rows
        if column is not None:
            names = [name for name, _, _ in self.fields]
            index = names.index(column)
            value = convert(value, self.fields[index][1])
        with open(self.file, "rb") as f:
            while True:
                raw = f.read(self.row_size)
                if len(raw) < self.row_size:
                    break
                alive, *values = struct.unpack(self.pattern, raw)
                if not alive:
                    continue
                row = [clean(v) for v in values]
                if column is None or compare(row[index], op, value):
                    rows.append(row)
        return rows


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