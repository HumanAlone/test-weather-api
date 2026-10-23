export interface GeoLocation {
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
