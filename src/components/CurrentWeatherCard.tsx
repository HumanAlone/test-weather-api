import { CurrentWeather } from '../types/weather';
import { getWeatherDescription, getWeatherIcon } from '../utils/weatherCodes';

interface CurrentWeatherCardProps {
  weather: CurrentWeather;
  cityName: string;
  country: string;
}

export default function CurrentWeatherCard({ weather, cityName, country }: CurrentWeatherCardProps) {
  return (
    <div className="text-center text-white mb-8">
      <div className="text-lg opacity-80 mb-1">
        📍 {cityName}, {country}
      </div>
      <div className="text-7xl mb-4">{getWeatherIcon(weather.weathercode)}</div>
      <div className="text-8xl font-thin mb-2">
        {Math.round(weather.temperature)}°C
      </div>
      <div className="text-2xl font-light mb-4">
        {getWeatherDescription(weather.weathercode)}
      </div>
      <div className="text-lg opacity-80">
        Ощущается как {Math.round(weather.apparent_temperature)}°C
      </div>
      
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
