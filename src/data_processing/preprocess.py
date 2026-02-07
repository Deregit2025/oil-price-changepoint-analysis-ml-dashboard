import numpy as np

def compute_log_returns(df, price_col='Price'):
    df['log_return'] = np.log(df[price_col] / df[price_col].shift(1))
    df.dropna(inplace=True)
    return df
