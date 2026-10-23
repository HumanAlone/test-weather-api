import { DailyForecast } from '../types/weather';
import { getWeatherDescription, getWeatherIcon, getDayName } from '../utils/weatherCodes';

interface DailyForecastCardProps {
  daily: DailyForecast[];
}

export default function DailyForecastCard({ daily }: DailyForecastCardProps) {
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-3xl p-6 border border-white/20">
      <h3 className="text-white text-lg font-medium mb-4 flex items-center gap-2">
        <span>📅</span> Прогноз на 7 дней
      </h3>
      <div className="space-y-2">
        {daily.map((day, i) => (
          <div
            key={i}
            className="flex items-center justify-between bg-white/5 hover:bg-white/15 rounded-2xl px-4 py-3 transition-colors"
          >
            <div className="flex items-center gap-3 w-32">
              <span className="text-white font-medium text-sm">{getDayName(day.date)}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{getWeatherIcon(day.weathercode)}</span>
              <span className="text-white/70 text-sm hidden sm:inline">
                {getWeatherDescription(day.weathercode)}
              </span>
            </div>
            <div className="flex items-center gap-4">
              {day.precipitation_sum > 0 && (
                <span className="text-blue-300 text-sm">
                  💧{day.precipitation_sum.toFixed(1)}мм
                </span>
              )}
              <div className="flex items-center gap-2">
                <span className="text-white font-medium">{Math.round(day.tempMax)}°</span>
                <span className="text-white/50">{Math.round(day.tempMin)}°</span>
              </div>
              <div className="w-20 h-2 rounded-full bg-white/10 overflow-hidden hidden sm:block">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-400 to-orange-400"
                  style={{
                    marginLeft: `${((day.tempMin + 10) / 50) * 100}%`,
                    width: `${((day.tempMax - day.tempMin) / 50) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
