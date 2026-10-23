import { GeoLocation, WeatherData, DailyForecast, HourlyForecast } from '../types/weather';

const GEO_API = 'https://geocoding-api.open-meteo.com/v1/search';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';

export async function searchCity(query: string): Promise<GeoLocation[]> {
  if (!query.trim()) return [];
  
  const response = await fetch(
    `${GEO_API}?name=${encodeURIComponent(query)}&count=5&language=ru&format=json`
  );
  
  if (!response.ok) throw new Error('Ошибка поиска города');
  
  const data = await response.json();
  return data.results || [];
}

export async function getWeather(location: GeoLocation): Promise<WeatherData> {
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

  // Get next 24 hours
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

  return {
    current,
    daily,
    hourly,
    location,
  };
}
