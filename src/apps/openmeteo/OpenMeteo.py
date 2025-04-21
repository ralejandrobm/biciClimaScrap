import openmeteo_requests
import os
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime


class OpenMeteo:
    ciudades = {
        "Guadalajara": (20.659698, -103.349609),
        "Zapopan": (20.671955, -103.416504),
        "Tlaquepaque": (20.64091, -103.29327)
    }

    def start(self):
        for ciudad, coordenadas in self.ciudades.items():
            if not self.consulta_api(coordenadas[0], coordenadas[1], ciudad):
                print(f"Error al obtener los datos para {ciudad}.")

    def consulta_api(self, latitude, longitude, ciudad):
        mes = {"1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril", "5": "Mayo", "6": "Junio", "7": "Julio",
               "8": "Agosto", "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"}
        current_date = datetime.now().strftime('%Y')
        dir_assets = 'assets'
        carpeta_raiz = 'datos_clima'
        carpeta_ciudad = ciudad
        folder = os.path.join(dir_assets, carpeta_raiz, carpeta_ciudad, current_date)
        os.makedirs(folder, exist_ok=True)

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        start_date = datetime(datetime.today().year, 1, 1).date()
        end_date = datetime.today().date()
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "precipitation_probability", "wind_speed_10m", "uv_index",
                       "uv_index_clear_sky", "is_day", "sunshine_duration", "direct_radiation"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration",
                      "sunshine_duration", "uv_index_max", "uv_index_clear_sky_max", "precipitation_probability_max"],
            "start_date": start_date,
            "end_date": end_date,
            "forecast_days": 0
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
        hourly_uv_index = hourly.Variables(3).ValuesAsNumpy()
        hourly_uv_index_clear_sky = hourly.Variables(4).ValuesAsNumpy()
        hourly_is_day = hourly.Variables(5).ValuesAsNumpy()
        hourly_sunshine_duration = hourly.Variables(6).ValuesAsNumpy()
        hourly_direct_radiation = hourly.Variables(7).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["uv_index"] = hourly_uv_index
        hourly_data["uv_index_clear_sky"] = hourly_uv_index_clear_sky
        hourly_data["is_day"] = hourly_is_day
        hourly_data["sunshine_duration"] = hourly_sunshine_duration
        hourly_data["direct_radiation"] = hourly_direct_radiation

        # El dataframe se crea y se agrega la columna 'month' para poder agrupar los datos por mes
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        hourly_dataframe['month'] = hourly_dataframe['date'].dt.month

        # print(hourly_dataframe)

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_sunrise = daily.Variables(2).ValuesAsNumpy()
        daily_sunset = daily.Variables(3).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(5).ValuesAsNumpy()
        daily_uv_index_max = daily.Variables(6).ValuesAsNumpy()
        daily_uv_index_clear_sky_max = daily.Variables(7).ValuesAsNumpy()
        daily_precipitation_probability_max = daily.Variables(8).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["uv_index_max"] = daily_uv_index_max
        daily_data["uv_index_clear_sky_max"] = daily_uv_index_clear_sky_max
        daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

        # El dataframe se crea y se agrega la columna 'month' para poder agrupar los datos por mes
        daily_dataframe = pd.DataFrame(data=daily_data)
        daily_dataframe['month'] = daily_dataframe['date'].dt.month

        # print(daily_dataframe)

        hourly_data_by_month = hourly_dataframe.groupby('month')
        daily_data_by_month = daily_dataframe.groupby('month')

        if hourly_dataframe.empty and daily_dataframe.empty:
            print("No se obtuvieron datos de la API.")
            return False
        else:
            print(f"Datos de {ciudad} obtenidos correctamente.\n")
            for month, data in hourly_data_by_month:
                # Crea una nueva carpeta para el mes
                month_folder = os.path.join(folder, f'{current_date}_{month}_{mes[str(month)]}')
                os.makedirs(month_folder, exist_ok=True)

                data.to_csv(os.path.join(month_folder, f'hourly_data_{current_date}_{month}.csv'), index=False)

            for month, data in daily_data_by_month:
                # Crea una nueva carpeta para el mes
                month_folder = os.path.join(folder, f'{current_date}_{month}_{mes[str(month)]}')
                os.makedirs(month_folder, exist_ok=True)

                data.to_csv(os.path.join(month_folder, f'daily_data_{current_date}_{month}.csv'), index=False)
            return True

if __name__ == "__main__":
    scrapmibici = OpenMeteo()
    scrapmibici.start()