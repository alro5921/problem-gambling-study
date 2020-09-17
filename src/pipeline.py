import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import random
from pipeline_constants import ALL_PRODUCTS, HAS_HOLD_DATA
from pipeline_constants import DEMO_PATH, RG_PATH, GAM_PATH
from sklearn.model_selection import train_test_split

WEIGHTS = {1: 1.0, 2: 1.9, 3: 1.6735638473207348, 4: 31.13842146476165, 5: 0.37584047124601383, 6: 11.056054972301116, 7: 8.64537708901529, 8: 47.617995276059325, 9: 0.527813110874204, 10: 15.031850760307305, 14: 7.697540618623065, 15: 18.24468154334213, 16: 1.1159477201340313, 17: 14.374133782112049, 19: 2.4441030442308227, 20: 2.8551162436493667, 21: 0.16649220018128694, 22: 0.4018520349820394, 23: 1.0120550412810625, 24: 0.20724743373917726, 25: 15.583412806157366}

def get_demo_df(path=DEMO_PATH):
    df = pd.read_csv(path, index_col='user_id')
    # date_cols = ['registration_date', 'first_deposit_date']
    # df[date_cols] = pd.to_datetime(df[date_cols])
    return df

def get_gam_df(path=GAM_PATH):
    df = pd.read_csv(path)
    df = apply_weighted_bets(df, w_means=WEIGHTS)
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

def learn_weighted_bets(gam_df, products=ALL_PRODUCTS):
    '''Aggregates the 'num_bets' across activities into a weighted one
    reflecting their actual activity implied'''
    mask = gam_df['num_bets_1'] > 0
    mean_1 = gam_df[mask]['num_bets_1'].mean()
    w_means = {1: mean_1}
    for prod in products:
        mask = gam_df[f'num_bets_{prod}'] > 0
        w_means[prod] = gam_df[mask][f'num_bets_{prod}'].mean()/mean_1
    return w_means

def apply_weighted_bets(gam_df, w_means, products=ALL_PRODUCTS):
    gam_df['weighted_bets'] = 0
    for prod in products:
        gam_df['weighted_bets'] += gam_df[f'num_bets_{prod}'] / w_means[prod]
    return gam_df

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
    demo_df = get_demo_df(path=DEMO_PATH)
    gam_df = pd.read_csv(GAM_PATH)
    weights = learn_weighted_bets(gam_df)
    print(weights)