import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline
from Featurizer import Featurizer

DEFAULT_CUTOFFS = ['2008-02-01','2008-05-01','2008-08-01', '2008-11-01', '2009-02-05','2009-05-01','2009-08-01']
DEFAULT_CUTOFFS = [np.datetime64(date) for date in DEFAULT_CUTOFFS]

demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

'''FEATURE MAKERS'''
def total_hold(frame):
    return frame['hold'].sum()

def max_hold(frame):
    return frame['hold'].max()

def total_activity(frame):
    return frame['weighted_bets'].sum()

def weekly_hold(frame, lookback):
    weekly_sum = frame.resample('W').sum()
    weekly_sum = pad_lookback(weekly_sum, lookback)
    return weekly_sum['hold'].values[-lookback:]

def rolling_hold(frame, lookback):
    weekly_sum = frame.resample('W').sum()
    pad_lookback(weekly_sum, lookback)
    return weekly_sum['weighted_bets'].rolling(5).sum()[4:][-lookback:]

def daily_rolling_hold(frame, lookback):
    frame = pad_lookback(frame, lookback)
    return frame['hold'].rolling(5).sum()[4:][-lookback:]

def total_fixed_live_ratio(frame):
    fixed_hold, live_action_hold = frame['hold_1'].sum(), frame['hold_2'].sum()
    if fixed_hold == 0:
        return 10
    return min(live_action_hold/fixed_hold, 10)

def weekly_fixed_live_ratio(frame, lookback):
    weekly_sum = frame.resample('M').sum()
    weekly_sum = pad_lookback(weekly_sum, lookback)
    return weekly_sum['turnover_2']/(1+weekly_sum['turnover'])

def pad_lookback(aggregate, lookback):
    pad = lookback - len(aggregate)
    if pad > 0:
        aggregate.append(aggregate.iloc[[-1]*pad])
    return aggregate

def make_default_featurizer():
    featurizer = Featurizer()
    featurizer.add_feature("total_hold", total_hold)
    featurizer.add_feature("max_hold", max_hold)
    featurizer.add_feature("rolling_hold", rolling_hold)
    featurizer.add_feature("weekly_hold", weekly_hold, {"lookback" : 52})
    featurizer.add_feature("rolling_hold", rolling_hold, {"lookback" : 52})
    featurizer.add_feature("daily_rolling_hold", daily_rolling_hold, {"lookback" : 180})
    featurizer.add_feature("weekly_fixed_live_ratio", weekly_fixed_live_ratio, {"lookback" : 52})
    featurizer.add_feature("total_fixed_live_ratio", total_fixed_live_ratio)
    return featurizer

def featurize(user_ids, featurizer=None, features=None):
    if not featurizer:
        featurizer = make_default_featurizer()
    frames, rgs = [], []
    for user_id in user_ids:
        products = [1,2,4]
        user_ts = pipeline.to_daily_ts(gam_df, user_id, product_types = products)
        user_ts = user_ts.fillna(0)
        rg_date = get_rg_date(user_id, demo_df, rg_info)
        for frame, rg in create_frames(user_ts, rg_date):
            frames.append(frame), rgs.append(rg)
    return featurizer.vectorize(frames, features), rgs

def get_rg_date(user_id, demo_info, rg_info):
    rg_date = None
    if demo_info.loc[user_id, 'rg'] == 1:
        rg_date = rg_info.loc[user_id, 'first_date']
    return rg_date

def create_timeframe(user_ids, has_rg, look_forward=3):
   pass     

def create_frames(user_ts, rg_date, look_back=24, look_forward=12, cutoffs = DEFAULT_CUTOFFS):
    '''Creates the frames from the user's time series data'''
    if rg_date == pd.Timestamp('NaT'):
        return []
    frames = []
    for cutoff in cutoffs:
        if rg_date:
            if rg_date < cutoff:
                break # Dont' want to include an RG event in the frame itself
            upcoming_rg = rg_date < (cutoff + np.timedelta64(look_forward * 30, 'D'))
        else:
            upcoming_rg = False
        frame = user_ts[cutoff - np.timedelta64(look_back * 30,'D'):cutoff]
        frames.append((frame,int(upcoming_rg)))
    return frames

if __name__ == '__main__':
    featurizer = make_default_featurizer()
    user_ids = [2062223, 912480, 3789290, 5313473, 5296662]
    vector, rgs = featurize(user_ids, featurizer, features=["total_hold", "weekly_hold", "daily_rolling_hold"])
    print(len(vector), len(rgs), len(vector[0]))