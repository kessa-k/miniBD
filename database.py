import os
from table import Table


class Database:
    def __init__(self, folder):
        self.folder = folder
        self.schema = os.path.join(folder, "schema.txt")
        self.tables = {}
        os.makedirs(folder, exist_ok=True)
        if os.path.exists(self.schema):
            with open(self.schema, encoding="utf-8") as f:
                for line in f:
                    words = line.split()
                    if words:
                        self.add_table(words[0], words[1:])

    def add_table(self, name, specs):
        fields = []
        for spec in specs:
            parts = spec.split(":")
            field_name = parts[0]
            kind = parts[1].upper()
            is_key = len(parts) > 2 and parts[2].upper() == "PK"
            fields.append((field_name, kind, is_key))
        self.tables[name] = Table(name, fields, self.folder)

    def create_table(self, name, specs):
        self.add_table(name, specs)
        with open(self.schema, "a", encoding="utf-8") as f:
            f.write(name + " " + " ".join(specs) + "\n")