import pandas as pd

def load_brent_prices(file_path="../data/raw/BrentOilPrices.csv"):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def load_detected_events(file_path="../data/processed/detected_events.csv"):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df.sort_values('Date', inplace=True)
    return df
