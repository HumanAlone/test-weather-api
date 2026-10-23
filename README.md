# 🌤️ Weather App — Погодное приложение

Веб-приложение для отображения погоды с Python-бэкендом (FastAPI) и React-фронтендом.

## 📁 Структура проекта

```
├── server.py            # Python API (FastAPI)
├── requirements.txt     # Зависимости Python
├── src/                 # React фронтенд
│   ├── App.tsx          # Главный компонент
│   ├── components/      # UI-компоненты
│   ├── services/        # API-клиент
│   ├── types/           # TypeScript типы
│   └── utils/           # Утилиты
├── package.json         # Зависимости Node.js
└── index.html           # Точка входа
```

## 🚀 Быстрый запуск

### 1. Запуск Python API

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите сервер
python server.py
```

Сервер запустится на `http://localhost:8000`  
Документация API (Swagger): `http://localhost:8000/docs`

### 2. Запуск фронтенда (для разработки)

```bash
# Установите зависимости
npm install

# Запустите dev-сервер
npm run dev
```

### 3. Продакшн-сборка (фронтенд + API вместе)

```bash
# Соберите фронтенд
npm run build

# Запустите Python API — он будет раздавать и API, и фронтенд
python server.py
```

Откройте `http://localhost:8000` в браузере.

## 📡 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/search?query=Москва` | Поиск города по названию |
| GET | `/api/weather?lat=55.75&lon=37.62` | Погода по координатам |
| GET | `/api/health` | Проверка работоспособности |

### Пример ответа `/api/weather`

```json
{
  "current": {
    "temperature": 22.5,
    "humidity": 65,
    "apparent_temperature": 24.1,
    "weather_code": 2,
    "wind_speed": 12.3,
    "pressure": 1013.2,
    "time": "2024-01-15T14:00"
  },
  "daily": [...],
  "hourly": [...]
}
```

## 🔧 Технологии

- **Backend:** Python 3.10+, FastAPI, httpx
- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
- **Данные:** [Open-Meteo API](https://open-meteo.com/) (бесплатно, без ключа)

## 📝 Примечания

- Фронтенд работает и без Python-бэкенда (обращается напрямую к Open-Meteo)
- С бэкендом — все запросы идут через `/api/*`
- Python-сервер в продакшн-режиме раздаёт собранный фронтенд
