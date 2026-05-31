# IT Knowledge Base Portal — Prototype

## Запуск (3 шага, PostgreSQL не нужен)

### 1. Установи зависимости

Открой терминал в папке `kb_portal` и выполни:

```
pip install -r requirements.txt
```

### 2. Заполни базу данных (создаётся автоматически)

```
python scripts/seed.py
```

Создаётся файл `kb_portal.db` (SQLite) — никаких настроек не нужно.

### 3. Запусти сервер

```
python run.py
```

Открой браузер: **http://localhost:8000**

---

## Логины

| Роль  | Логин   | Пароль    |
|-------|---------|-----------|
| Admin | `admin` | `Admin123!` |
| User  | `jsmith` | `User123!` |

Админ-панель: **http://localhost:8000/admin/**

---

## Что есть в прототипе

- Главная страница с поиском и категориями
- Поиск по статьям (ключевые слова + фильтр по категории)
- 8 категорий: Network/VPN, Account/Access, Email, Printers, Hardware, Software, Security, Mobile
- 8 готовых статей с пошаговыми решениями
- Страница статьи: шаги, код, callout-блоки, кнопка "Was this helpful?"
- Админ-панель: создание/редактирование/удаление статей и категорий
- Авторизация с ролями (user / admin)
