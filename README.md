# 🌤️ Weather App — Погодное приложение

Простое погодное приложение на Python (FastAPI) + чистый HTML/JS.

## 🚀 Быстрый запуск

```bash
# 1. Создайте виртуальное окружение (опционально)
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Запустите!
python server.py
```

Откройте **http://localhost:8000** в браузере. **Всё!** 🎉

## 📁 Структура проекта

```
├── server.py            # Python API (FastAPI)
├── requirements.txt     # Зависимости Python
├── static/
│   └── index.html       # Фронтенд (HTML + JS + Tailwind CDN)
└── README.md
```

## 📡 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Главная страница (фронтенд) |
| GET | `/api/search?query=Москва` | Поиск города |
| GET | `/api/weather?lat=55.75&lon=37.62` | Погода по координатам |
| GET | `/api/health` | Проверка работоспособности |
| GET | `/docs` | Swagger-документация |

## 🔧 Технологии

- **Backend:** Python 3.10+, FastAPI, httpx
- **Frontend:** Чистый HTML + JavaScript + Tailwind CSS (через CDN)
- **Данные:** [Open-Meteo API](https://open-meteo.com/) (бесплатно, без ключа)

## ✅ Преимущества

- ❌ Не нужен Node.js
- ❌ Не нужен npm
- ❌ Не нужна сборка
- ✅ Только Python
- ✅ Запуск одной командой
