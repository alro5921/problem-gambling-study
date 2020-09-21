import numpy as np
import pandas as pd
from pipeline_constants import ALL_PRODUCTS, HAS_HOLD_DATA, WEIGHTS
from pipeline_constants import DEMO_PATH, RG_PATH, GAM_PATH
from sklearn.model_selection import train_test_split

def get_demo_df(path=DEMO_PATH):
    df = pd.read_csv(path, index_col='user_id')
    return df

def get_gam_df(path=GAM_PATH):
    df = pd.read_csv(path)
    df = apply_weighted_bets(df, weights=WEIGHTS)
    # Need to recast datetime after writing to a csv
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_rg_df(path=RG_PATH):
    df = pd.read_csv(path, index_col='user_id')
    return df

def get_user_ids(demo_df):
    return list(demo_df.index)

def sparse_to_ts(user_daily, date_start=None, date_end=None, window=None):
    '''Converts the user's sparse, daily data into a time series over a specified time window'''
    if not date_start and not date_end:
        print("Need to specify an anchor point if using a gap.")
        raise ValueError
    if date_start and not date_end:
        date_end = np.datetime64(date_start) + np.timedelta64(window, 'D')
    if not date_start and date_end:
        date_start = np.datetime64(date_end) - np.timedelta64(window, 'D')
        
    date_indexed = user_daily.set_index('date',drop=True)
    idx = pd.date_range(date_start, date_end)
    user_ts = date_indexed.reindex(idx, fill_value=0)
    return user_ts

def learn_weighted_bets(gam_df, products=ALL_PRODUCTS):
    '''
    Aggregates the 'num_bets' across activities into a weighted one
    reflecting their actual activity implied
    '''
    mask = gam_df['num_bets_1'] > -1
    mean_1 = gam_df[mask]['num_bets_1'].mean()
    w_means = {1: mean_1}
    for prod in products:
        mask = gam_df[f'num_bets_{prod}'] > -1
        w_means[prod] = gam_df[mask][f'num_bets_{prod}'].mean()/mean_1
    return w_means

def apply_weighted_bets(gam_df, weights, products=ALL_PRODUCTS):
    '''Applies learned weights to all rows'''
    gam_df['weighted_bets'] = 0
    for prod in products:
        gam_df['weighted_bets'] += gam_df[f'num_bets_{prod}'] / weights[prod]
    return gam_df

if __name__ == '__main__':
    demo_df = get_demo_df(path=DEMO_PATH)
    gam_df = pd.read_csv(GAM_PATH)
    weights = learn_weighted_bets(gam_df)
    print(weights)