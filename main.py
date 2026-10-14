from database import Database

db = Database("data")
print("MiniDB готова. Команды: create, insert, select, exit")

while True:
    words = input("minidb> ").split()
    if not words:
        continue
    command = words[0].lower()
    try:
        if command == "exit":
            break
        elif command == "create":
            db.create_table(words[1], words[2:])
            print("таблица", words[1], "создана")
        elif command == "insert":
            db.tables[words[1]].insert(words[2:])
            print("запись добавлена")
        elif command == "select":
            table = db.tables[words[1]]
            if len(words) > 2 and words[2].lower() == "where":
                rows = table.select(words[3], words[4],words[5])
            else:
                rows = table.select()
            for row in rows:
                print(row)
        else:
            print("не знаю такой команды")
    except Exception as e:
        print("ошибка:", e)