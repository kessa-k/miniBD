# MiniDB

## Запуск

```bash
git clone <ссылка на репозиторий>
cd miniBD
python3 main.py
```

Программа открывает базу в папке `data/` и ждёт команды после приглашения `minidb>`.


### Команды

Части команды разделяются пробелами, поэтому значения пишутся без пробелов
(например, `question_answering`). Операторы условия: `=`, `!=`, `>`, `<`, `>=`, `<=`.

**create** — создать таблицу

```
create <таблица> <поле>:<ТИП>[:PK | :FK:<таблица>] ...
```

```
create datasets id:INT:PK name:STRING task:STRING size:INT
create models id:INT:PK name:STRING version:STRING
create experiments id:INT:PK dataset_id:INT:FK:datasets model_id:INT:FK:models accuracy:FLOAT status:STRING
```

**insert** — добавить запись (значения в порядке полей; id можно не указывать)

```
insert <таблица> <значение> <значение> ...
```

```
insert datasets 6 PetFaces face_swap 2500
insert datasets PetFaces face_swap 2500
insert experiments 2 3 0.87 completed
```

**select** — показать все записи или записи по условию

```
select <таблица>
select <таблица> where <поле> <оператор> <значение>
```

```
select experiments
select experiments where accuracy > 0.9
select experiments where status = running
```

**update** — изменить поле в записях, подходящих под условие

```
update <таблица> set <поле> = <значение> where <поле> <оператор> <значение>
```

```
update experiments set status = completed where id = 3
update experiments set accuracy = 0.5 where status = failed
```

**delete** — удалить записи, подходящие под условие

```
delete <таблица> where <поле> <оператор> <значение>
```

```
delete experiments where status = crying
delete experiments where id = 7
```

**exit** — выйти из программы

```
exit
```

## Архитектура

```
miniBD/
├── main.py        консоль: разбирает команду и вызывает Database / Table
├── database.py    класс Database: все таблицы, схема, проверка внешних ключей
├── table.py       класс Table: один файл таблицы, упаковка записей, CRUD
└── data/
    ├── schema.txt         описание таблиц (текст)
    ├── datasets.taib      записи datasets (байты)
    ├── models.taib        записи models (байты)
    └── experiments.taib   записи experiments (байты)
```

## Реализованные функции

**Хранение**
- Собственные файлы: схема в `schema.txt`, записи в бинарных файлах `.taib`
  (модуль `struct`).
- Схема и данные сохраняются после перезапуска программы.

**Таблицы и типы**
- `CREATE TABLE` с именем таблицы, полями, типами, PRIMARY KEY и FOREIGN KEY.
- Типы `INT`, `FLOAT`, `STRING`.

**Операции**
- `INSERT` — добавление записи.
- `SELECT` — все записи или записи по условию с операторами `=`, `!=`, `>`, `<`, `>=`, `<=`.
- `UPDATE` — изменение поля у записей по условию.
- `DELETE` — удаление записей по условию.

**PRIMARY KEY**
- Запрет дублей: нельзя добавить запись с уже существующим id.
- Авто-ID: если id не указан, назначается `max(id) + 1`.
- Запрет изменения PK через `UPDATE`.

**Внешние ключи**
- Связи `experiments.dataset_id → datasets.id` и `experiments.model_id → models.id`.
- Нельзя добавить или изменить эксперимент со ссылкой на несуществующий датасет или модель