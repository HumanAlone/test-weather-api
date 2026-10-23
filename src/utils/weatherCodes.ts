export function getWeatherDescription(code: number): string {
  const descriptions: Record<number, string> = {
    0: 'Ясно',
    1: 'Преимущественно ясно',
    2: 'Переменная облачность',
    3: 'Пасмурно',
    45: 'Туман',
    48: 'Изморозь',
    51: 'Лёгкая морось',
    53: 'Умеренная морось',
    55: 'Сильная морось',
    61: 'Небольшой дождь',
    63: 'Умеренный дождь',
    65: 'Сильный дождь',
    66: 'Ледяной дождь',
    67: 'Сильный ледяной дождь',
    71: 'Небольшой снег',
    73: 'Умеренный снег',
    75: 'Сильный снег',
    77: 'Снежные зёрна',
    80: 'Лёгкий ливень',
    81: 'Умеренный ливень',
    82: 'Сильный ливень',
    85: 'Небольшой снегопад',
    86: 'Сильный снегопад',
    95: 'Гроза',
    96: 'Гроза с градом',
    99: 'Сильная гроза с градом',
  };
  return descriptions[code] || 'Неизвестно';
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
  if (code >= 85 && code <= 86) return '🌨️';
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

  const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
  return days[date.getDay()];
}
