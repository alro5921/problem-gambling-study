import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline

# Global variables weeee
demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

DEFAULT_CUTOFFS = ['2008-02-01','2008-05-01','2008-08-01', '2008-11-01', '2009-02-05','2009-05-01','2009-08-01']
DEFAULT_CUTOFFS = [np.datetime64(date) for date in DEFAULT_CUTOFFS]

'''This all needs to be refactored, it's completely hamstrung feature selection and model changing
Part of it is that the frames more complicated than a DF (it's FOUR Dfs oooooo) but still. 
First thing I'm doing Cap 3 is rewriting/tearing this down to be not terrible.'''


def add_cumulative(series, col='hold', cum_name=None):
    if not name:
        name = col + '_cum'
    series[cum_name] = series[col].cumsum()
    return series

def featurize(users):
    '''Converts the user_id set into model-ready featurized frames'''
    rows = []
    rgs = []
    for user_id in users:
        user_rows, user_rgs = featurize_user(user_id)
        for row, rg in zip(user_rows, user_rgs):
            rows.append(row)
            rgs.append(rg)
    print("Done featurizing this chunk")
    print(f"Vectorized Length: {len(row)}")
    return np.array(rows), np.array(rgs)

def featurize_user(user_id):
    '''Features a particular user''' 
    rows = []
    upcoming_rg = []
    rg_date = None
    if demo_df.loc[user_id, 'rg'] == 1:
        rg_date = rg_info.loc[user_id, 'first_date']
    all_products = list(range(1,30))
    user_ts = pipeline.accum_by_date(gam_df, user_id, product_types = all_products)
    user_sets = create_frames(user_ts, rg_date)
    fixed_live_rat = fixed_live_ratio(user_id)
    for ts, rg in user_sets:
        age = 2009 - demo_df.loc[user_id, 'birth_year'] #From a different table than ts
        max_hold = ts['hold'].max()
        total_hold = ts['hold'].sum()
        total_activity = ts['weighted_bets'].sum()
        # row = [total_activity]
        row = [age, max_hold, total_hold, fixed_live_rat, *featurize_set(ts)]
        # row = [*featurize_set(ts)]
        rows.append(row)
        upcoming_rg.append(rg)
    return rows, upcoming_rg

def featurize_set(set_ts):
    '''Features a particular frame'''
    max_hold = set_ts['hold'].max()
    total_hold = set_ts['hold'].sum()
    weekly_sum = set_ts.resample('W').sum()
    if(len(weekly_sum) != 104):
        print(f'Date {set_ts.index[-1]} is still messing up damn')
    weight_series = weekly_sum['weighted_bets'].values
    hold_series = weekly_sum['hold'].values
    rolling_bets = weekly_sum['weighted_bets'].rolling(5).sum()[4:]
    return [*weight_series, *hold_series, *rolling_bets]

def to_weekly(user_ts):
    week = user_ts.resample('W').sum()
    return week

def fixed_live_ratio(user_id):
    '''
    Calculates fixed bet odds to live bet odds ratio
    Note: Fairly poorly done and leaky, need to actually restrict to the frame
    '''
    mask = (gam_df['user_id'] == user_id) & (gam_df['date'] < '2008-11-01')
    user = gam_df[mask]
    holds = user.groupby('product_type').sum()['hold']
    if not 1 in holds.index:
        return 15
    elif not 2 in holds.index:
        return 0
    else:
        return min(15, holds[2]/holds[1])

def create_frames(user_ts, rg_date, look_back=24, look_forward=12, cutoffs = DEFAULT_CUTOFFS):
    '''Creates the frames from the user's time series data'''
    if rg_date == pd.Timestamp('NaT'):
        return []
    sets = []
    for cutoff in cutoffs:
        if rg_date:
            if rg_date < cutoff:
                break # Dont' want to include an RG event in the frame itself
            upcoming_rg = rg_date < (cutoff + np.timedelta64(look_forward * 30, 'D'))
        else:
            upcoming_rg = False
        user_12_month = user_ts[cutoff - np.timedelta64(look_back * 30,'D'):cutoff]
        sets.append((user_12_month,int(upcoming_rg)))
    return sets

if __name__ == '__main__':
    user_id = 3327778
    ts = pipeline.accum_by_date(gam_df, user_id)
    sets = create_frames(ts, np.datetime64('NaT'))
    #breakpoint()
    #print(list(s[1] for s in sets))
    #user_ids = [2062223, 912480, 3789290]
    no_rg_ids = list(demo_df[demo_df['rg'] == 0].index)[:100]
    print(featurize(no_rg_ids)[1])