import { GeoLocation, WeatherData, DailyForecast, HourlyForecast } from '../types/weather';

// Базовый URL API (Python бэкенд). Если бэкенд недоступен — фолбэк на прямые запросы.
const API_BASE = '/api';

// Флаг: проверен ли доступ к бэкенду
let backendAvailable: boolean | null = null;

async function checkBackend(): Promise<boolean> {
  if (backendAvailable !== null) return backendAvailable;
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
    backendAvailable = res.ok;
  } catch {
    backendAvailable = false;
  }
  return backendAvailable;
}

// ===== Прямые запросы к Open-Meteo (фолбэк) =====
const GEO_API = 'https://geocoding-api.open-meteo.com/v1/search';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';

async function searchCityDirect(query: string): Promise<GeoLocation[]> {
  const response = await fetch(
    `${GEO_API}?name=${encodeURIComponent(query)}&count=10&language=ru&format=json`
  );
  if (!response.ok) throw new Error('Ошибка поиска города');
  const data = await response.json();
  return (data.results || []).map((c: any) => ({
    id: c.id,
    name: c.name,
    latitude: c.latitude,
    longitude: c.longitude,
    country: c.country || '',
    admin1: c.admin1 || '',
  }));
}

async function getWeatherDirect(location: GeoLocation): Promise<WeatherData> {
  const params = new URLSearchParams({
    latitude: location.latitude.toString(),
    longitude: location.longitude.toString(),
    current: 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
    hourly: 'temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m',
    daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
    timezone: 'auto',
    forecast_days: '7',
  });

  const response = await fetch(`${WEATHER_API}?${params}`);
  if (!response.ok) throw new Error('Ошибка получения погоды');
  const data = await response.json();

  const current = {
    temperature: data.current.temperature_2m,
    windspeed: data.current.wind_speed_10m,
    weathercode: data.current.weather_code,
    time: data.current.time,
    relative_humidity_2m: data.current.relative_humidity_2m,
    apparent_temperature: data.current.apparent_temperature,
  };

  const daily: DailyForecast[] = data.daily.time.map((date: string, i: number) => ({
    date,
    tempMax: data.daily.temperature_2m_max[i],
    tempMin: data.daily.temperature_2m_min[i],
    weathercode: data.daily.weather_code[i],
    precipitation_sum: data.daily.precipitation_sum[i],
    windspeed_max: data.daily.wind_speed_10m_max[i],
  }));

  const now = new Date();
  const currentHourIndex = data.hourly.time.findIndex((t: string) => new Date(t) >= now);
  const startIdx = Math.max(0, currentHourIndex);

  const hourly: HourlyForecast[] = data.hourly.time
    .slice(startIdx, startIdx + 24)
    .map((time: string, i: number) => ({
      time,
      temperature: data.hourly.temperature_2m[startIdx + i],
      weathercode: data.hourly.weather_code[startIdx + i],
      windspeed: data.hourly.wind_speed_10m[startIdx + i],
      humidity: data.hourly.relative_humidity_2m[startIdx + i],
    }));

  return { current, daily, hourly, location };
}

// ===== Запросы через Python API =====
async function searchCityViaApi(query: string): Promise<GeoLocation[]> {
  const response = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Ошибка поиска города');
  const data = await response.json();
  return (data.results || []).map((c: any) => ({
    id: c.id,
    name: c.name,
    latitude: c.latitude,
    longitude: c.longitude,
    country: c.country || '',
    admin1: c.admin1 || '',
  }));
}

async function getWeatherViaApi(location: GeoLocation): Promise<WeatherData> {
  const response = await fetch(
    `${API_BASE}/weather?lat=${location.latitude}&lon=${location.longitude}`
  );
  if (!response.ok) throw new Error('Ошибка получения погоды');
  const data = await response.json();

  const current = {
    temperature: data.current.temperature,
    windspeed: data.current.wind_speed,
    weathercode: data.current.weather_code,
    time: data.current.time,
    relative_humidity_2m: data.current.humidity,
    apparent_temperature: data.current.apparent_temperature,
  };

  const daily: DailyForecast[] = data.daily.map((d: any) => ({
    date: d.date,
    tempMax: d.temp_max,
    tempMin: d.temp_min,
    weathercode: d.weather_code,
    precipitation_sum: d.precipitation,
    windspeed_max: d.wind_max,
  }));

  const hourly: HourlyForecast[] = data.hourly.map((h: any) => ({
    time: h.time,
    temperature: h.temperature,
    weathercode: h.weather_code,
    windspeed: h.wind_speed,
    humidity: h.humidity,
  }));

  return { current, daily, hourly, location };
}

// ===== Публичные функции (с автоопределением источника) =====
export async function isBackendAvailable(): Promise<boolean> {
  return checkBackend();
}

export async function searchCity(query: string): Promise<GeoLocation[]> {
  if (query.length < 2) return [];
  const useApi = await checkBackend();
  return useApi ? searchCityViaApi(query) : searchCityDirect(query);
}

export async function getWeather(location: GeoLocation): Promise<WeatherData> {
  const useApi = await checkBackend();
  return useApi ? getWeatherViaApi(location) : getWeatherDirect(location);
}
