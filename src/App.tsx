import { useState, useEffect } from 'react';
import CitySearch from './components/CitySearch';
import CurrentWeatherCard from './components/CurrentWeatherCard';
import HourlyForecastCard from './components/HourlyForecastCard';
import DailyForecastCard from './components/DailyForecastCard';
import { getWeather, isBackendAvailable } from './services/weatherApi';
import { getWeatherGradient } from './utils/weatherCodes';
import { WeatherData, GeoLocation } from './types/weather';

const DEFAULT_CITY: GeoLocation = {
  id: 524901,
  name: 'Москва',
  latitude: 55.7558,
  longitude: 37.6173,
  country: 'Россия',
};

export default function App() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingBackend, setUsingBackend] = useState<boolean | null>(null);

  const fetchWeather = async (location: GeoLocation) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getWeather(location);
      setWeather(data);
      setUsingBackend(await isBackendAvailable());
    } catch (err) {
      setError('Не удалось загрузить данные о погоде. Попробуйте позже.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather(DEFAULT_CITY);
  }, []);

  const handleCitySelect = (location: GeoLocation) => {
    fetchWeather(location);
  };

  const gradientClass = weather
    ? getWeatherGradient(weather.current.weathercode)
    : 'from-blue-500 via-blue-400 to-cyan-300';

  return (
    <div className={`min-h-screen bg-gradient-to-br ${gradientClass} transition-all duration-1000`}>
      <div className="min-h-screen bg-black/10 backdrop-blur-sm">
        {/* Header */}
        <header className="pt-8 pb-4 px-4">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-white text-3xl font-light text-center mb-6">
              🌤️ Погода
            </h1>
            <div className="flex justify-center">
              <CitySearch onSelect={handleCitySelect} />
            </div>
            
            {/* Индикатор источника данных */}
            <div className="flex justify-center mt-3">
              {usingBackend === true && (
                <span className="inline-flex items-center gap-1.5 text-xs text-green-200 bg-green-500/20 px-3 py-1 rounded-full border border-green-400/30">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Python API подключён
                </span>
              )}
              {usingBackend === false && (
                <span className="inline-flex items-center gap-1.5 text-xs text-yellow-200 bg-yellow-500/20 px-3 py-1 rounded-full border border-yellow-400/30">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  Прямое подключение к Open-Meteo (запустите server.py для Python API)
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="max-w-4xl mx-auto px-4 pb-12">
          {loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-16 h-16 border-4 border-white/30 border-t-white rounded-full animate-spin mb-4"></div>
              <p className="text-white/80 text-lg">Загрузка погоды...</p>
            </div>
          )}

          {error && !loading && (
            <div className="bg-red-500/20 backdrop-blur-md border border-red-300/30 rounded-3xl p-8 text-center">
              <span className="text-4xl mb-4 block">⚠️</span>
              <p className="text-white text-lg">{error}</p>
              <button
                onClick={() => fetchWeather(DEFAULT_CITY)}
                className="mt-4 px-6 py-2 bg-white/20 hover:bg-white/30 rounded-xl text-white transition-colors"
              >
                Попробовать снова
              </button>
            </div>
          )}

          {weather && !loading && !error && (
            <div className="space-y-6 animate-fade-in">
              <CurrentWeatherCard
                weather={weather.current}
                cityName={weather.location.name}
                country={weather.location.country}
              />
              <HourlyForecastCard hourly={weather.hourly} />
              <DailyForecastCard daily={weather.daily} />
              
              <div className="text-center text-white/50 text-sm pt-4">
                Данные: Open-Meteo API • Обновлено: {new Date(weather.current.time).toLocaleString('ru-RU')}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
