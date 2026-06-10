# 🏠 Риелтор-бот для Telegram

Умный бот на базе Claude AI — консультирует клиентов по недвижимости как живой риелтор.

---

## 🚀 Быстрый старт

### Шаг 1 — Создай бота в Telegram
1. Открой Telegram, найди @BotFather
2. Напиши `/newbot`
3. Придумай имя (например: `Консультант по недвижимости`)
4. Придумай username (например: `moi_realty_bot`)
5. Скопируй токен вида `1234567890:AAF...` — это твой `TELEGRAM_BOT_TOKEN`

### Шаг 2 — Получи ключ Anthropic API
1. Зарегистрируйся на https://console.anthropic.com
2. Перейди в API Keys → Create Key
3. Скопируй ключ вида `sk-ant-...` — это твой `ANTHROPIC_API_KEY`

### Шаг 3 — Запусти на Railway (бесплатно)

**Railway** даёт $5 в месяц бесплатно — этого хватает для бота.

1. Зарегистрируйся на https://railway.app (через GitHub)
2. Нажми **New Project → Deploy from GitHub repo**
3. Загрузи файлы бота в GitHub репозиторий
4. В Railway перейди в **Variables** и добавь:
   ```
   TELEGRAM_BOT_TOKEN = твой_токен
   ANTHROPIC_API_KEY = твой_ключ
   ```
5. Railway сам установит зависимости и запустит бота

**Альтернатива — Render.com:**
1. Зарегистрируйся на https://render.com
2. New → Web Service → подключи GitHub
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python bot.py`
5. Добавь переменные окружения

---

## 💻 Локальный запуск (для теста)

```bash
# Установи зависимости
pip install -r requirements.txt

# Создай .env файл
cp .env.example .env
# Открой .env и вставь свои ключи

# Запусти бота
python bot.py
```

---

## 📝 Как обновить базу ЖК

В файле `bot.py` найди переменную `REALTY_DATABASE` и редактируй её:

```python
REALTY_DATABASE = """
1. ЖК Название, застройщик
   - Цена: от XX млн
   - Условия: ...
   - Подходит: ...
"""
```

После обновления просто перезапусти бота.

---

## 🤖 Команды бота

- `/start` — начать диалог
- `/reset` — начать заново (сброс истории)

---

## 📁 Структура проекта

```
realty_bot/
├── bot.py          # Основной код бота
├── requirements.txt # Зависимости
├── .env.example    # Шаблон переменных окружения
└── README.md       # Эта инструкция
```
