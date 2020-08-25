import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline

demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()
#lookback = 6 months
#rg_lookahead = 3 months


def add_cumulative(series, col = 'hold', cum_name = None):
    if not name:
        name = col + '_cum'
    series[cum_name] = series[col].cumsum()
    return series

def featurize(users):
    rows = []
    rgs = []
    for user_id in users:
        user_rows, user_rgs = featurize_user(user_id)
        for row in user_rows:
            rows.append(row)
        for rg in user_rgs:
            rgs.append(rg)
    return np.array(rows), np.array(rgs)

def featurize_user(user_id):
    rows = []
    upcoming_rg = []
    rg_date = None
    if demo_df.loc[user_id, 'rg'] == 1:
        rg_date = rg_info.loc[user_id, 'first_date']
    user_ts = pipeline.accum_by_date(gam_df, user_id)
    user_sets = create_sets(user_ts, rg_date)
    for ts, rg in user_sets:
        age = 2009 - demo_df.loc[user_id, 'birth_year'] 
        max_hold = ts['hold'].max()
        total_hold = ts['hold'].sum()
        weekly_sum = ts.resample('W').sum()
        hold_series = weekly_sum['hold'].values
        row = [age, max_hold, total_hold, *hold_series]
        rows.append(row)
        upcoming_rg.append(rg)
    return rows, upcoming_rg
    
        #wbet_series = weekly_sum['weighted_bets']


def to_weekly(user_ts):
    week = user_ts.resample('W').sum()
    return week

def create_sets(user_ts, rg_date):
    sets = []
    cutoffs = ['2008-08-01', '2008-11-01', '2009-02-01','2009-05-01','2009-08-01','2009-11-01', '2010-02-01']
    cutoffs = [np.datetime64(date) for date in cutoffs]
    for cutoff in cutoffs:
        if rg_date:
            if rg_date < cutoff:
                break #Dont' want to include an RG event in the frame itself
            upcoming_rg = rg_date < (cutoff + np.timedelta64(180, 'D'))
        else:
            upcoming_rg = False
        user_12_month = user_ts[cutoff - np.timedelta64(360,'D'):cutoff]
        sets.append((user_12_month,int(upcoming_rg)))
    return sets

if __name__ == '__main__':
    user_id = 2062223
    ts = pipeline.accum_by_date(gam_df, user_id)
    sets = create_sets(ts, np.datetime64('2009-06-08'))
    #print(list(s[1] for s in sets))
    user_ids = [2062223, 912480, 3789290]
    print(featurize(user_ids))