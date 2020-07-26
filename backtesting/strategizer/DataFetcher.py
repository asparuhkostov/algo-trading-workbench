import pandas as pd
import requests


class DataFetcher:
    def get_symbol_OHLC_data(
        self, 
        data_provider_settings, 
        filename, 
        asset_symbol,
        source
    ):
        full_filename = asset_symbol + "_" + filename
        api_response = None
        
        if source == "alpha_vantage_api":
            api_response = requests.get(f'{data_provider_settings["ALPHA_VANTAGE_API_URL"]}{data_provider_settings["ALPHA_VANTAGE_FUNCTION"]}&symbol={asset_symbol}&apikey={data_provider_settings["ALPHA_VANTAGE_API_KEY"]}&outputsize={data_provider_settings["ALPHA_VANTAGE_TIME_SERIES_LENGTH"]}&datatype=csv')
        if source == "internal_web_scraping_service":
            api_response = requests.get(f'http://localhost:2000/getSymbolOHLCTimeSeries/{asset_symbol}')        
        data_file = open(full_filename, 'wb')
        data_file.write(api_response.content)
            

        df = pd.read_csv(
            full_filename, 
            sep = ',',
            parse_dates = ["timestamp"]
        )
        df = df.dropna(subset = ["timestamp"])
        pd.to_datetime(df["timestamp"])
        return df


    def get_period_of_time_series(
        self, 
        data, 
        start_date, 
        end_date
    ):
        data_after_start_date = data[data["timestamp"] > pd.Timestamp(start_date)]
        data_until_end_date = data_after_start_date[data_after_start_date["timestamp"] < pd.Timestamp(end_date)]
        return data_until_end_date.drop_duplicates()