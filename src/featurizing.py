import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline
from Featurizer import Featurizer

demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

'''Functions that convert the daily trend into features'''
def total_hold(frame):
    return frame['hold'].sum()

def max_hold(frame):
    return frame['hold'].max()

def total_activity(frame):
    return frame['weighted_bets'].sum()

def weekly_hold(frame, lookback):
    weekly_sum = frame.resample('W').sum()
    if len(weekly_sum) < lookback:
        pad_length = lookback - len(weekly_sum)
        weekly_sum.append(weekly_sum.iloc[[-1]*pad_length])
    return weekly_sum['hold'].values[-lookback:]

def rolling_hold(frame, lookback):
    '''Doesn't actually use lookback yet l'''
    weekly_sum = frame.resample('W').sum()
    return weekly_sum['weighted_bets'].rolling(5).sum()[4:]

featurizer = Featurizer()
featurizer.add_feature("total_hold", total_hold)
featurizer.add_feature("max_hold", max_hold)
featurizer.add_feature("rolling_hold", rolling_hold)
featurizer.add_feature("weekly_hold", weekly_hold, {"lookback" : 26})
featurizer.add_feature("rolling_hold", weekly_hold, {"lookback" : 26})

# def to_weekly(user_ts, lookback=None):
#     week = user_ts.resample('W').sum()
#     return week

def featurize(user_ids, features=None):
    frames, rgs = [], []
    for user_id in user_ids:
        all_products = list(range(1,30))
        user_ts = pipeline.accum_by_date(gam_df, user_id, product_types = all_products)
        rg_date = get_rg_date(user_id, demo_df, rg_info)
        for frame, rg in create_frames(user_ts, rg_date):
            frames.append(frame), rgs.append(rg)
    return featurizer.vectorize(frames, features), rgs

def get_rg_date(user_id, demo_info, rg_info):
    rg_date = None
    if demo_info.loc[user_id, 'rg'] == 1:
        rg_date = rg_info.loc[user_id, 'first_date']
    return rg_date

DEFAULT_CUTOFFS = ['2008-02-01','2008-05-01','2008-08-01', '2008-11-01', '2009-02-05','2009-05-01','2009-08-01']
DEFAULT_CUTOFFS = [np.datetime64(date) for date in DEFAULT_CUTOFFS]

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
    user_ids = [2062223, 912480, 3789290, 5313473, 5296662]
    vector, rgs = featurize(user_ids, features=["total_hold", "weekly_hold"])
    print(len(vector), len(rgs), len(vector[0]))