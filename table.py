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
            if kind == "INT":
                row.append(int(value))
            elif kind == "FLOAT":
                row.append(float(value))
            else:
                row.append(value.encode("utf-8"))
        with open(self.file, "ab") as f:
            f.write(struct.pack(self.pattern, *row))

    def select(self):
        rows = []
        if not os.path.exists(self.file):
            return rows
        with open(self.file, "rb") as f:
            while True:
                raw = f.read(self.row_size)
                if len(raw) < self.row_size:
                    break
                alive, *values = struct.unpack(self.pattern, raw)
                if alive:
                    rows.append([clean(v) for v in values])
        return rows


def clean(value):
    if isinstance(value, bytes):
        return value.rstrip(b"\x00").decode("utf-8")
    return value