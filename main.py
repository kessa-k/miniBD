from database import Database

db = Database("data")
print("MiniDB готова. Команды: create, insert, select, update, delete, exit")

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
            new_id = db.insert(words[1], words[2:])
            print("запись добавлена, id =", new_id)
        elif command == "select":
            table = db.table(words[1])
            if len(words) > 2 and words[2].lower() == "where":
                rows = table.select(words[3], words[4],words[5])
            else:
                rows = table.select()
            for row in rows:
                print(row)
        elif command == "delete":
            count = db.table(words[1]).delete(words[3], words[4], words[5])
            print("удалено записей:", count)
        elif command == "update":
            count = db.update(words[1], words[3], words[5], words[7], words[8], words[9])
            print("изменено записей:", count)
        else:
            print("не знаю такой команды")
    except IndexError:
        print("ошибка: команда неполная")
    except ValueError as e:
        print("ошибка:", e)
    except Exception as e:
        print("непредвиденная ошибка:", e)