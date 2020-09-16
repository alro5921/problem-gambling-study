import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import random
from pipeline_constants import ALL_PRODUCTS, HAS_HOLD_DATA
from pipeline_constants import DEMO_PATH, RG_PATH, GAM_PATH
from sklearn.model_selection import train_test_split

def get_demo_df(path=DEMO_PATH):
    df = pd.read_csv(path, index_col='user_id')
    # date_cols = ['registration_date', 'first_deposit_date']
    # df[date_cols] = pd.to_datetime(df[date_cols])
    return df

def get_gam_df(path=GAM_PATH):
    df = pd.read_csv(path)
    df = add_weighted_bets(df)
    # Writing to csv reverts the datetime cast
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_rg_df(path=RG_PATH):
    df = pd.read_csv(path, index_col='user_id')
    # date_cols = ['first_date', 'last_date']
    # df[date_cols] = pd.to_datetime(df[date_cols])
    return df

def get_user_ids(demo_df):
    return list(demo_df.index)

#1305631
def sparse_to_ts(user_daily, date_start=None, date_end=None, window=None):
    '''Converts the user's sparse, daily data into a time series over a specified time window'''
    if not date_start and not date_end:
        print("Need to specify an anchor point if using a gap")
        return -1
    if date_start and not date_end:
        date_end = np.datetime64(date_start) + np.timedelta64(window, 'D')
    if not date_start and date_end:
        date_start = np.datetime64(date_end) - np.timedelta64(window, 'D')
        
    date_indexed = user_daily.set_index('date',drop=True)
    idx = pd.date_range(date_start, date_end)
    user_ts = date_indexed.reindex(idx, fill_value=0)
    return user_ts

def add_weighted_bets(gam_df, w_means=None, products=ALL_PRODUCTS):
    '''Aggregates the 'num_bets' across activities into a weighted one
    reflecting their actual activity implied'''
    if not w_means:
        mean_1 = gam_df['num_bets_1'].mean()
        w_means = {prod: gam_df[f'num_bets_{prod}'].mean()/mean_1 
                    for prod in products}
    gam_df['weighted_bets'] = 0
    for prod in products:
        gam_df['weighted_bets'] += gam_df[f'num_bets_{prod}'] / w_means[prod]
    return gam_df

def filter_low_activity(frames, activity_thres=10):
    '''I'm deferring on a activity-based prediction
    until a certain level of activity is actually seen'''
    return [frame for frame in frames 
            if frame['weighted_bets'].sum() > activity_thres]

def oversample(user_ids, demo_df):
    demo_filt = demo_df[demo_df.index.isin(user_ids)]
    rg_ids = list(demo_filt[demo_filt['rg'] == 1].index)
    no_rg_ids = list(demo_filt[demo_filt['rg'] == 0].index)
    return rg_ids + random.choices(no_rg_ids, k=len(rg_ids))

if __name__ == '__main__':
    demo_df = get_demo_df(demo_path=DEMO_PATH)
    breakpoint()