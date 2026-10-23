import { HourlyForecast } from '../types/weather';
import { getWeatherIcon } from '../utils/weatherCodes';

interface HourlyForecastCardProps {
  hourly: HourlyForecast[];
}

export default function HourlyForecastCard({ hourly }: HourlyForecastCardProps) {
  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    return `${date.getHours().toString().padStart(2, '0')}:00`;
  };

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-3xl p-6 border border-white/20">
      <h3 className="text-white text-lg font-medium mb-4 flex items-center gap-2">
        <span>🕐</span> Почасовой прогноз
      </h3>
      <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
        {hourly.map((hour, i) => (
          <div
            key={i}
            className="flex flex-col items-center min-w-[70px] bg-white/10 rounded-2xl p-3 hover:bg-white/20 transition-colors"
          >
            <span className="text-white/70 text-sm mb-2">{formatTime(hour.time)}</span>
            <span className="text-2xl mb-2">{getWeatherIcon(hour.weathercode)}</span>
            <span className="text-white font-medium">{Math.round(hour.temperature)}°</span>
            <span className="text-white/50 text-xs mt-1">💧{hour.humidity}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
