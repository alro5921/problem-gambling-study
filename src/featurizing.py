import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline
from Featurizer import Featurizer
from features import (total_hold, max_hold, total_activity, weekly_activity,
                    weekly_hold, weekly_rolling_hold, daily_rolling_hold,
                    total_fixed_live_ratio, weekly_fixed_live_ratio)

DEFAULT_CUTOFFS = ['2008-02-01','2008-05-01','2008-08-01', '2008-11-01', '2009-02-05','2009-05-01','2009-08-01']
DEFAULT_CUTOFFS = [np.datetime64(date) for date in DEFAULT_CUTOFFS]

demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

def make_default_featurizer():
    featurizer = Featurizer()
    featurizer.add_feature(total_hold)
    featurizer.add_feature(max_hold)
    featurizer.add_feature(total_activity)
    featurizer.add_feature(weekly_activity, args={"lookback" : 25})
    featurizer.add_feature(weekly_hold, args={"lookback" : 25})
    featurizer.add_feature(weekly_rolling_hold, args={"lookback" : 25})
    featurizer.add_feature(daily_rolling_hold, args={"lookback" : 150})
    featurizer.add_feature(weekly_fixed_live_ratio, args={"lookback" : 25})
    featurizer.add_feature(total_fixed_live_ratio)
    return featurizer

def featurize(user_ids, featurizer=None, features=None):
    print("Starting frame making")
    if not featurizer:
        featurizer = make_default_featurizer()
    frames, rgs = [], []
    for user_id in user_ids:
        products = [1,2,8,10,16]
        user_ts = pipeline.to_daily_ts(gam_df, user_id, product_types=products)
        user_ts = user_ts.fillna(0)
        rg_date = get_rg_date(user_id, demo_df, rg_info)
        for frame, rg in create_frames(user_ts, rg_date):
            frames.append(frame), rgs.append(rg)
    return featurizer.vectorize(frames, features), rgs

def featurize_forward(user_ids, featurizer=None, features=None, look_forward=12):
    print("Starting frame making")
    if not featurizer:
        featurizer = make_default_featurizer()
    frames, rgs = [], []
    for user_id in user_ids:
        products = [1,2,8,10,16]
        user_ts = pipeline.to_daily_ts(gam_df, user_id, product_types=products)
        user_ts = user_ts.fillna(0)
        frame, rg = create_timeframe(user_ts, user_id, look_forward)
        frames.append(frame)
        rgs.append(rg)
    return featurizer.vectorize(frames, features), rgs

def get_rg_date(user_id, demo_info, rg_info):
    rg_date = None
    if demo_info.loc[user_id, 'rg'] == 1:
        rg_date = rg_info.loc[user_id, 'first_date']
    return rg_date

#TODO: Just get the user from the ts
def create_timeframe(user_ts, user_id, look_forward=12):
    first_deposit = demo_df.loc[user_id, 'first_deposit_date']
    frame = user_ts[first_deposit : first_deposit + np.timedelta64(look_forward * 30, 'D')]
    return frame, demo_df.loc[user_id, 'rg'] == 1


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
    vector, rgs = featurize_forward(user_ids, featurizer, features=["total_hold", "weekly_hold", "daily_rolling_hold"])
    print(len(vector), len(rgs), len(vector[0]))