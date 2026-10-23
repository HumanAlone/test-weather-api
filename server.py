"""
Weather API Server
==================
Бэкенд на FastAPI для получения данных о погоде.
Использует бесплатный Open-Meteo API (не требует ключа).

Запуск:
    pip install -r requirements.txt
    uvicorn server:app --reload --port 8000

Эндпоинты:
    GET /api/search?query=Москва       — поиск города
    GET /api/weather?lat=55.75&lon=37.62 — погода по координатам
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import os
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Weather API", version="1.0.0")

# CORS — разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Внешние API
GEO_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

# Таймаут для внешних запросов
TIMEOUT = 10.0


@app.get("/api/search")
async def search_city(query: str = Query(..., min_length=1, description="Название города")):
    """
    Поиск города по названию.
    Возвращает список совпадений с координатами.
    """
    logger.info(f"🔍 Поиск города: {query}")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                GEO_API,
                params={
                    "name": query,
                    "count": 10,
                    "language": "ru",
                    "format": "json",
                },
            )
            logger.info(f"📡 Ответ от геокодера: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"❌ Ошибка геокодирования: {response.status_code}")
            raise HTTPException(status_code=502, detail="Ошибка сервиса геокодирования")
    except httpx.RequestError as e:
        logger.error(f"❌ Ошибка запроса к геокодеру: {e}")
        raise HTTPException(status_code=502, detail=f"Ошибка соединения: {str(e)}")

    data = response.json()
    results = data.get("results", [])

    # Форматируем ответ
    cities = []
    for city in results:
        cities.append({
            "id": city.get("id"),
            "name": city.get("name"),
            "latitude": city.get("latitude"),
            "longitude": city.get("longitude"),
            "country": city.get("country", ""),
            "admin1": city.get("admin1", ""),
            "population": city.get("population", 0),
        })

    return {"results": cities}


@app.get("/api/weather")
async def get_weather(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
):
    """
    Получение погоды по координатам.
    Возвращает текущую погоду, почасовой и дневной прогноз.
    """
    logger.info(f"🌡️ Запрос погоды: lat={lat}, lon={lon}")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                WEATHER_API,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,pressure_msl",
                    "hourly": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunrise,sunset",
                    "timezone": "auto",
                    "forecast_days": 7,
                },
            )
            logger.info(f"📡 Ответ от weather API: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"❌ Ошибка weather API: {response.status_code}")
            raise HTTPException(status_code=502, detail="Ошибка сервиса погоды")
    except httpx.RequestError as e:
        logger.error(f"❌ Ошибка запроса к weather API: {e}")
        raise HTTPException(status_code=502, detail=f"Ошибка соединения: {str(e)}")

    data = response.json()

    # --- Формируем текущую погоду ---
    current_raw = data.get("current", {})
    current = {
        "temperature": current_raw.get("temperature_2m"),
        "humidity": current_raw.get("relative_humidity_2m"),
        "apparent_temperature": current_raw.get("apparent_temperature"),
        "weather_code": current_raw.get("weather_code"),
        "wind_speed": current_raw.get("wind_speed_10m"),
        "pressure": current_raw.get("pressure_msl"),
        "time": current_raw.get("time"),
    }

    # --- Формируем дневной прогноз ---
    daily_raw = data.get("daily", {})
    daily_times = daily_raw.get("time", [])
    daily = []
    for i, date in enumerate(daily_times):
        daily.append({
            "date": date,
            "temp_max": daily_raw["temperature_2m_max"][i],
            "temp_min": daily_raw["temperature_2m_min"][i],
            "weather_code": daily_raw["weather_code"][i],
            "precipitation": daily_raw["precipitation_sum"][i],
            "wind_max": daily_raw["wind_speed_10m_max"][i],
            "sunrise": daily_raw.get("sunrise", [None] * len(daily_times))[i],
            "sunset": daily_raw.get("sunset", [None] * len(daily_times))[i],
        })

    # --- Формируем почасовой прогноз (ближайшие 24 часа) ---
    hourly_raw = data.get("hourly", {})
    hourly_times = hourly_raw.get("time", [])

    # Находим текущий час
    from datetime import datetime
    now = datetime.now()
    start_idx = 0
    for i, t in enumerate(hourly_times):
        if datetime.fromisoformat(t) >= now:
            start_idx = i
            break

    hourly = []
    for i in range(start_idx, min(start_idx + 24, len(hourly_times))):
        hourly.append({
            "time": hourly_times[i],
            "temperature": hourly_raw["temperature_2m"][i],
            "weather_code": hourly_raw["weather_code"][i],
            "wind_speed": hourly_raw["wind_speed_10m"][i],
            "humidity": hourly_raw["relative_humidity_2m"][i],
        })

    return {
        "current": current,
        "daily": daily,
        "hourly": hourly,
        "timezone": data.get("timezone", "auto"),
    }


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности сервера."""
    return {"status": "ok", "message": "Weather API работает!"}


# --- Раздача статических файлов фронтенда ---
# Фронтенд лежит в папке static/ (чистый HTML+JS, не требует сборки)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def serve_index():
        """Главная страница."""
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Раздаём фронтенд для всех не-API маршрутов."""
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("🌤️  Weather API запускается на http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    print("🌐 Фронтенд: http://localhost:8000")
    print("\n✅ Готово! Откройте http://localhost:8000 в браузере\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
