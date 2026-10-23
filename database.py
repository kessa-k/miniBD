import os
from table import Table, CODES


class Database:
    def __init__(self, folder):
        self.folder = folder
        self.schema = os.path.join(folder, "schema.txt")
        self.tables = {}
        self.refs = {}
        os.makedirs(folder, exist_ok=True)

        if os.path.exists(self.schema):
            with open(self.schema, encoding="utf-8") as f:
                for line in f:
                    words = line.split()
                    if words:
                        self.add_table(words[0], words[1:])

    def add_table(self, name, specs):
        if not specs:
            raise ValueError("у таблицы должно быть хотя бы одно поле")
        fields = []
        refs = {}
        for spec in specs:
            parts = spec.split(":")
            if len(parts) < 2:
                raise ValueError(f"{spec}: поле пишется как имя:ТИП, имя:ТИП:PK или имя:ТИП:FK:таблица")
            field_name = parts[0]
            kind = parts[1].upper()
            if kind not in CODES:
                raise ValueError(f"{spec}: тип может быть только INT, FLOAT или STRING")
            extra = parts[2].upper() if len(parts) > 2 else ""
            is_key = extra == "PK"
            if extra == "FK":
                if len(parts) < 4:
                    raise ValueError(f"{spec}: внешний ключ пишется как имя:ТИП:FK:таблица")
                parent = parts[3]
                if parent not in self.tables:
                    raise ValueError(f"{spec}: таблицы {parent} нет, сначала создай её")
                if self.tables[parent].key is None:
                    raise ValueError(f"{spec}: у таблицы {parent} нет PK, ссылаться не на что")
                refs[field_name] = parent
            fields.append((field_name, kind, is_key))
        self.tables[name] = Table(name, fields, self.folder)
        self.refs[name] = refs

    def create_table(self, name, specs):
        if name in self.tables:
            raise ValueError(f"таблица {name} уже есть")
        self.add_table(name, specs)
        with open(self.schema, "a", encoding="utf-8") as f:
            f.write(name + " " + " ".join(specs) + "\n")

    def table(self, name):
        if name not in self.tables:
            raise ValueError(f"таблицы {name} нет")
        return self.tables[name]

    def check_ref(self, field, value, parent_name):
        parent = self.tables[parent_name]
        key_name = parent.names[parent.key]
        if not parent.find(key_name, "=", value):
            raise ValueError(f"{field}={value}: в таблице {parent_name} нет записи с {key_name}={value}")

    def insert(self, name, values):
        table = self.table(name)
        values = table.complete(values)
        for field, parent_name in self.refs[name].items():
            value = values[table.column(field)]
            self.check_ref(field, value, parent_name)
        return table.insert(values)

    def update(self, name, set_column, new_value, column, op, value):
        table = self.table(name)
        if set_column in self.refs[name]:
            self.check_ref(set_column, new_value, self.refs[name][set_column])
        return table.update(set_column, new_value, column, op, value)