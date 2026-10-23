#!/usr/bin/env python3
"""
Установщик Weather App
======================
Этот скрипт воссоздаёт весь проект Weather App.
Просто запустите: python create_project.py

После запуска:
    cd weather-app
    pip install -r requirements.txt
    python server.py
"""

import os
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather-app")

FILES = {
    # ===== requirements.txt =====
    "requirements.txt": """fastapi==0.115.0
uvicorn[standard]==0.30.6
httpx==0.27.2
""",

    # ===== server.py =====
    "server.py": '''"""
Weather API Server
==================
Бэкенд на FastAPI для получения данных о погоде.
Запуск: pip install -r requirements.txt && python server.py
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import os

app = FastAPI(title="Weather API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEO_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10.0


@app.get("/api/search")
async def search_city(query: str = Query(..., min_length=1)):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            GEO_API,
            params={"name": query, "count": 10, "language": "ru", "format": "json"},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Ошибка сервиса геокодирования")
    data = response.json()
    cities = []
    for city in data.get("results", []):
        cities.append({
            "id": city.get("id"),
            "name": city.get("name"),
            "latitude": city.get("latitude"),
            "longitude": city.get("longitude"),
            "country": city.get("country", ""),
            "admin1": city.get("admin1", ""),
        })
    return {"results": cities}


@app.get("/api/weather")
async def get_weather(
    lat: float = Query(...),
    lon: float = Query(...),
):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            WEATHER_API,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "hourly": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                "timezone": "auto",
                "forecast_days": 7,
            },
        )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Ошибка сервиса погоды")
    data = response.json()

    current_raw = data.get("current", {})
    current = {
        "temperature": current_raw.get("temperature_2m"),
        "humidity": current_raw.get("relative_humidity_2m"),
        "apparent_temperature": current_raw.get("apparent_temperature"),
        "weather_code": current_raw.get("weather_code"),
        "wind_speed": current_raw.get("wind_speed_10m"),
        "time": current_raw.get("time"),
    }

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
        })

    hourly_raw = data.get("hourly", {})
    hourly_times = hourly_raw.get("time", [])
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

    return {"current": current, "daily": daily, "hourly": hourly, "timezone": data.get("timezone", "auto")}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Weather API работает!"}


DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
if os.path.isdir(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("🌤️  Weather API: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',

    # ===== package.json =====
    "package.json": """{
  "name": "weather-app",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.5.3",
    "vite": "^5.3.4"
  }
}
""",

    # ===== index.html =====
    "index.html": """<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Погода — Прогноз для вашего города</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",

    # ===== vite.config.js =====
    "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
""",

    # ===== tsconfig.json =====
    "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
""",

    # ===== tailwind.config.js =====
    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
""",

    # ===== postcss.config.js =====
    "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",

    # ===== src/index.css =====
    "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
""",

    # ===== src/main.tsx =====
    "src/main.tsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",

    # ===== src/types/weather.ts =====
    "src/types/weather.ts": """export interface GeoLocation {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1?: string;
}

export interface CurrentWeather {
  temperature: number;
  windspeed: number;
  weathercode: number;
  time: string;
  relative_humidity_2m: number;
  apparent_temperature: number;
}

export interface DailyForecast {
  date: string;
  tempMax: number;
  tempMin: number;
  weathercode: number;
  precipitation_sum: number;
  windspeed_max: number;
}

export interface HourlyForecast {
  time: string;
  temperature: number;
  weathercode: number;
  windspeed: number;
  humidity: number;
}

export interface WeatherData {
  current: CurrentWeather;
  daily: DailyForecast[];
  hourly: HourlyForecast[];
  location: GeoLocation;
}
""",

    # ===== src/utils/weatherCodes.ts =====
    "src/utils/weatherCodes.ts": """export function getWeatherDescription(code: number): string {
  const d: Record<number, string> = {
    0: 'Ясно', 1: 'Преимущественно ясно', 2: 'Переменная облачность', 3: 'Пасмурно',
    45: 'Туман', 48: 'Изморозь', 51: 'Лёгкая морось', 53: 'Умеренная морось',
    55: 'Сильная морось', 61: 'Небольшой дождь', 63: 'Умеренный дождь', 65: 'Сильный дождь',
    71: 'Небольшой снег', 73: 'Умеренный снег', 75: 'Сильный снег', 80: 'Лёгкий ливень',
    81: 'Умеренный ливень', 82: 'Сильный ливень', 95: 'Гроза', 96: 'Гроза с градом', 99: 'Сильная гроза',
  };
  return d[code] || 'Неизвестно';
}

export function getWeatherIcon(code: number): string {
  if (code === 0) return '☀️';
  if (code === 1) return '🌤️';
  if (code === 2) return '⛅';
  if (code === 3) return '☁️';
  if (code === 45 || code === 48) return '🌫️';
  if (code >= 51 && code <= 55) return '🌦️';
  if (code >= 56 && code <= 67) return '🌧️';
  if (code >= 71 && code <= 77) return '🌨️';
  if (code >= 80 && code <= 82) return '🌧️';
  if (code >= 95) return '⛈️';
  return '🌡️';
}

export function getWeatherGradient(code: number): string {
  if (code === 0) return 'from-yellow-400 via-orange-400 to-blue-400';
  if (code <= 2) return 'from-blue-400 via-blue-300 to-yellow-200';
  if (code === 3) return 'from-gray-400 via-gray-500 to-blue-300';
  if (code === 45 || code === 48) return 'from-gray-300 via-gray-400 to-gray-500';
  if (code >= 51 && code <= 67) return 'from-blue-600 via-blue-500 to-gray-400';
  if (code >= 71 && code <= 86) return 'from-blue-200 via-blue-300 to-gray-300';
  if (code >= 95) return 'from-gray-700 via-purple-600 to-gray-800';
  return 'from-blue-400 via-blue-300 to-blue-200';
}

export function getDayName(dateStr: string): string {
  const date = new Date(dateStr);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  if (date.toDateString() === today.toDateString()) return 'Сегодня';
  if (date.toDateString() === tomorrow.toDateString()) return 'Завтра';
  return ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'][date.getDay()];
}
""",

    # ===== src/services/weatherApi.ts =====
    "src/services/weatherApi.ts": """import { GeoLocation, WeatherData, DailyForecast, HourlyForecast } from '../types/weather';

const API_BASE = '/api';
let backendAvailable: boolean | null = null;

async function checkBackend(): Promise<boolean> {
  if (backendAvailable !== null) return backendAvailable;
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
    backendAvailable = res.ok;
  } catch { backendAvailable = false; }
  return backendAvailable;
}

const GEO_API = 'https://geocoding-api.open-meteo.com/v1/search';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';

async function searchCityDirect(query: string): Promise<GeoLocation[]> {
  const r = await fetch(`${GEO_API}?name=${encodeURIComponent(query)}&count=10&language=ru&format=json`);
  const d = await r.json();
  return (d.results || []).map((c: any) => ({
    id: c.id, name: c.name, latitude: c.latitude, longitude: c.longitude,
    country: c.country || '', admin1: c.admin1 || '',
  }));
}

async function getWeatherDirect(loc: GeoLocation): Promise<WeatherData> {
  const p = new URLSearchParams({
    latitude: loc.latitude.toString(), longitude: loc.longitude.toString(),
    current: 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
    hourly: 'temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m',
    daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
    timezone: 'auto', forecast_days: '7',
  });
  const r = await fetch(`${WEATHER_API}?${p}`);
  const d = await r.json();
  const current = {
    temperature: d.current.temperature_2m, windspeed: d.current.wind_speed_10m,
    weathercode: d.current.weather_code, time: d.current.time,
    relative_humidity_2m: d.current.relative_humidity_2m,
    apparent_temperature: d.current.apparent_temperature,
  };
  const daily: DailyForecast[] = d.daily.time.map((dt: string, i: number) => ({
    date: dt, tempMax: d.daily.temperature_2m_max[i], tempMin: d.daily.temperature_2m_min[i],
    weathercode: d.daily.weather_code[i], precipitation_sum: d.daily.precipitation_sum[i],
    windspeed_max: d.daily.wind_speed_10m_max[i],
  }));
  const now = new Date();
  const idx = Math.max(0, d.hourly.time.findIndex((t: string) => new Date(t) >= now));
  const hourly: HourlyForecast[] = d.hourly.time.slice(idx, idx + 24).map((t: string, i: number) => ({
    time: t, temperature: d.hourly.temperature_2m[idx + i],
    weathercode: d.hourly.weather_code[idx + i],
    windspeed: d.hourly.wind_speed_10m[idx + i],
    humidity: d.hourly.relative_humidity_2m[idx + i],
  }));
  return { current, daily, hourly, location: loc };
}

async function searchCityViaApi(query: string): Promise<GeoLocation[]> {
  const r = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`);
  const d = await r.json();
  return (d.results || []).map((c: any) => ({
    id: c.id, name: c.name, latitude: c.latitude, longitude: c.longitude,
    country: c.country || '', admin1: c.admin1 || '',
  }));
}

async function getWeatherViaApi(loc: GeoLocation): Promise<WeatherData> {
  const r = await fetch(`${API_BASE}/weather?lat=${loc.latitude}&lon=${loc.longitude}`);
  const d = await r.json();
  const current = {
    temperature: d.current.temperature, windspeed: d.current.wind_speed,
    weathercode: d.current.weather_code, time: d.current.time,
    relative_humidity_2m: d.current.humidity,
    apparent_temperature: d.current.apparent_temperature,
  };
  const daily: DailyForecast[] = d.daily.map((x: any) => ({
    date: x.date, tempMax: x.temp_max, tempMin: x.temp_min,
    weathercode: x.weather_code, precipitation_sum: x.precipitation, windspeed_max: x.wind_max,
  }));
  const hourly: HourlyForecast[] = d.hourly.map((x: any) => ({
    time: x.time, temperature: x.temperature, weathercode: x.weather_code,
    windspeed: x.wind_speed, humidity: x.humidity,
  }));
  return { current, daily, hourly, location: loc };
}

export async function isBackendAvailable(): Promise<boolean> { return checkBackend(); }

export async function searchCity(query: string): Promise<GeoLocation[]> {
  if (query.length < 2) return [];
  return (await checkBackend()) ? searchCityViaApi(query) : searchCityDirect(query);
}

export async function getWeather(loc: GeoLocation): Promise<WeatherData> {
  return (await checkBackend()) ? getWeatherViaApi(loc) : getWeatherDirect(loc);
}
""",

    # ===== src/App.tsx =====
    "src/App.tsx": """import { useState, useEffect } from 'react';
import CitySearch from './components/CitySearch';
import CurrentWeatherCard from './components/CurrentWeatherCard';
import HourlyForecastCard from './components/HourlyForecastCard';
import DailyForecastCard from './components/DailyForecastCard';
import { getWeather, isBackendAvailable } from './services/weatherApi';
import { getWeatherGradient } from './utils/weatherCodes';
import { WeatherData, GeoLocation } from './types/weather';

const DEFAULT_CITY: GeoLocation = {
  id: 524901, name: 'Москва', latitude: 55.7558, longitude: 37.6173, country: 'Россия',
};

export default function App() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingBackend, setUsingBackend] = useState<boolean | null>(null);

  const fetchWeather = async (loc: GeoLocation) => {
    setLoading(true); setError(null);
    try {
      const data = await getWeather(loc);
      setWeather(data);
      setUsingBackend(await isBackendAvailable());
    } catch { setError('Не удалось загрузить погоду.'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchWeather(DEFAULT_CITY); }, []);

  const gradientClass = weather
    ? getWeatherGradient(weather.current.weathercode)
    : 'from-blue-500 via-blue-400 to-cyan-300';

  return (
    <div className={`min-h-screen bg-gradient-to-br ${gradientClass} transition-all duration-1000`}>
      <div className="min-h-screen bg-black/10 backdrop-blur-sm">
        <header className="pt-8 pb-4 px-4">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-white text-3xl font-light text-center mb-6">🌤️ Погода</h1>
            <div className="flex justify-center"><CitySearch onSelect={fetchWeather} /></div>
            <div className="flex justify-center mt-3">
              {usingBackend === true && (
                <span className="inline-flex items-center gap-1.5 text-xs text-green-200 bg-green-500/20 px-3 py-1 rounded-full border border-green-400/30">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Python API подключён
                </span>
              )}
              {usingBackend === false && (
                <span className="inline-flex items-center gap-1.5 text-xs text-yellow-200 bg-yellow-500/20 px-3 py-1 rounded-full border border-yellow-400/30">
                  Прямое подключение (запустите server.py для Python API)
                </span>
              )}
            </div>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-4 pb-12">
          {loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-16 h-16 border-4 border-white/30 border-t-white rounded-full animate-spin mb-4"></div>
              <p className="text-white/80 text-lg">Загрузка...</p>
            </div>
          )}
          {error && !loading && (
            <div className="bg-red-500/20 backdrop-blur-md border border-red-300/30 rounded-3xl p-8 text-center">
              <p className="text-white text-lg">{error}</p>
              <button onClick={() => fetchWeather(DEFAULT_CITY)}
                className="mt-4 px-6 py-2 bg-white/20 hover:bg-white/30 rounded-xl text-white">
                Попробовать снова
              </button>
            </div>
          )}
          {weather && !loading && !error && (
            <div className="space-y-6 animate-fade-in">
              <CurrentWeatherCard weather={weather.current} cityName={weather.location.name} country={weather.location.country} />
              <HourlyForecastCard hourly={weather.hourly} />
              <DailyForecastCard daily={weather.daily} />
              <div className="text-center text-white/50 text-sm pt-4">
                Обновлено: {new Date(weather.current.time).toLocaleString('ru-RU')}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
""",

    # ===== src/components/CitySearch.tsx =====
    "src/components/CitySearch.tsx": """import { useState, useEffect, useRef } from 'react';
import { GeoLocation } from '../types/weather';
import { searchCity } from '../services/weatherApi';

export default function CitySearch({ onSelect }: { onSelect: (l: GeoLocation) => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GeoLocation[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const ref = useRef<ReturnType<typeof setTimeout>>();
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setIsOpen(false);
    };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);

  useEffect(() => {
    if (ref.current) clearTimeout(ref.current);
    if (query.length < 2) { setResults([]); setIsOpen(false); return; }
    ref.current = setTimeout(async () => {
      setLoading(true);
      try { setResults(await searchCity(query)); setIsOpen(true); }
      catch { setResults([]); }
      finally { setLoading(false); }
    }, 300);
  }, [query]);

  return (
    <div ref={wrapRef} className="relative w-full max-w-md">
      <input type="text" value={query} onChange={e => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setIsOpen(true)}
        placeholder="🔍 Введите город..."
        className="w-full px-5 py-3 rounded-2xl bg-white/20 backdrop-blur-md border border-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50 text-lg" />
      {loading && <div className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 border-2 border-white/50 border-t-white rounded-full animate-spin"></div>}
      {isOpen && (
        <div className="absolute top-full mt-2 w-full bg-white/95 backdrop-blur-lg rounded-2xl shadow-2xl overflow-hidden z-50">
          {results.map(loc => (
            <button key={loc.id} onClick={() => { onSelect(loc); setQuery(`${loc.name}, ${loc.country}`); setIsOpen(false); }}
              className="w-full px-5 py-3 text-left hover:bg-blue-50 border-b border-gray-100 last:border-0">
              <div className="font-medium text-gray-800">{loc.name}</div>
              <div className="text-sm text-gray-500">{[loc.admin1, loc.country].filter(Boolean).join(', ')}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
""",

    # ===== src/components/CurrentWeatherCard.tsx =====
    "src/components/CurrentWeatherCard.tsx": """import { CurrentWeather } from '../types/weather';
import { getWeatherDescription, getWeatherIcon } from '../utils/weatherCodes';

export default function CurrentWeatherCard({ weather, cityName, country }: { weather: CurrentWeather; cityName: string; country: string }) {
  return (
    <div className="text-center text-white mb-8">
      <div className="text-lg opacity-80 mb-1">📍 {cityName}, {country}</div>
      <div className="text-7xl mb-4">{getWeatherIcon(weather.weathercode)}</div>
      <div className="text-8xl font-thin mb-2">{Math.round(weather.temperature)}°C</div>
      <div className="text-2xl font-light mb-4">{getWeatherDescription(weather.weathercode)}</div>
      <div className="text-lg opacity-80">Ощущается как {Math.round(weather.apparent_temperature)}°C</div>
      <div className="flex justify-center gap-8 mt-8">
        <div className="flex flex-col items-center bg-white/10 rounded-2xl px-6 py-4 backdrop-blur-sm">
          <span className="text-2xl mb-1">💨</span>
          <span className="text-sm opacity-70">Ветер</span>
          <span className="font-medium">{weather.windspeed} км/ч</span>
        </div>
        <div className="flex flex-col items-center bg-white/10 rounded-2xl px-6 py-4 backdrop-blur-sm">
          <span className="text-2xl mb-1">💧</span>
          <span className="text-sm opacity-70">Влажность</span>
          <span className="font-medium">{weather.relative_humidity_2m}%</span>
        </div>
        <div className="flex flex-col items-center bg-white/10 rounded-2xl px-6 py-4 backdrop-blur-sm">
          <span className="text-2xl mb-1">🌡️</span>
          <span className="text-sm opacity-70">Ощущается</span>
          <span className="font-medium">{Math.round(weather.apparent_temperature)}°C</span>
        </div>
      </div>
    </div>
  );
}
""",

    # ===== src/components/HourlyForecastCard.tsx =====
    "src/components/HourlyForecastCard.tsx": """import { HourlyForecast } from '../types/weather';
import { getWeatherIcon } from '../utils/weatherCodes';

export default function HourlyForecastCard({ hourly }: { hourly: HourlyForecast[] }) {
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-3xl p-6 border border-white/20">
      <h3 className="text-white text-lg font-medium mb-4">🕐 Почасовой прогноз</h3>
      <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
        {hourly.map((h, i) => (
          <div key={i} className="flex flex-col items-center min-w-[70px] bg-white/10 rounded-2xl p-3">
            <span className="text-white/70 text-sm mb-2">{new Date(h.time).getHours().toString().padStart(2,'0')}:00</span>
            <span className="text-2xl mb-2">{getWeatherIcon(h.weathercode)}</span>
            <span className="text-white font-medium">{Math.round(h.temperature)}°</span>
            <span className="text-white/50 text-xs mt-1">💧{h.humidity}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
""",

    # ===== src/components/DailyForecastCard.tsx =====
    "src/components/DailyForecastCard.tsx": """import { DailyForecast } from '../types/weather';
import { getWeatherDescription, getWeatherIcon, getDayName } from '../utils/weatherCodes';

export default function DailyForecastCard({ daily }: { daily: DailyForecast[] }) {
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-3xl p-6 border border-white/20">
      <h3 className="text-white text-lg font-medium mb-4">📅 Прогноз на 7 дней</h3>
      <div className="space-y-2">
        {daily.map((d, i) => (
          <div key={i} className="flex items-center justify-between bg-white/5 hover:bg-white/15 rounded-2xl px-4 py-3">
            <span className="text-white font-medium text-sm w-20">{getDayName(d.date)}</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{getWeatherIcon(d.weathercode)}</span>
              <span className="text-white/70 text-sm hidden sm:inline">{getWeatherDescription(d.weathercode)}</span>
            </div>
            <div className="flex items-center gap-4">
              {d.precipitation_sum > 0 && <span className="text-blue-300 text-sm">💧{d.precipitation_sum.toFixed(1)}мм</span>}
              <div className="flex items-center gap-2">
                <span className="text-white font-medium">{Math.round(d.tempMax)}°</span>
                <span className="text-white/50">{Math.round(d.tempMin)}°</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
""",
}


def create_file(rel_path: str, content: str):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {rel_path}")


def main():
    print(f"\n🌤️  Создание проекта Weather App в: {BASE_DIR}\n")

    if os.path.exists(BASE_DIR):
        print(f"⚠️  Папка {BASE_DIR} уже существует.")
        answer = input("   Перезаписать? (y/N): ").strip().lower()
        if answer != "y":
            print("Отменено.")
            sys.exit(0)
        import shutil
        shutil.rmtree(BASE_DIR)

    os.makedirs(BASE_DIR, exist_ok=True)

    for path, content in FILES.items():
        create_file(path, content)

    print(f"\n✅ Проект создан! {len(FILES)} файлов.")
    print(f"\n📋 Следующие шаги:")
    print(f"   cd {os.path.basename(BASE_DIR)}")
    print(f"   pip install -r requirements.txt")
    print(f"   npm install")
    print(f"   python server.py")
    print(f"\n🌐 Откройте http://localhost:8000")
    print(f"📖 API docs: http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
