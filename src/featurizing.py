import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline
from Featurizer import Featurizer
from features import (total_hold, max_hold, total_activity, weekly_activity,
                    weekly_hold, daily_rolling_hold,
                    total_fixed_live_ratio)
from pipeline import get_demo_df, get_gam_df, get_rg_df 
from pipeline import sparse_to_ts

demo_df = get_demo_df()
gam_df = get_gam_df()
rg_df = get_rg_df()

def make_default_featurizer(look_back=12):
    featurizer = Featurizer()
    featurizer.add_feature(total_hold)
    featurizer.add_feature(max_hold)
    featurizer.add_feature(total_activity)
    featurizer.add_feature(total_fixed_live_ratio)
    featurizer.add_feature(weekly_activity, args={"lookback" : look_back*4})
    featurizer.add_feature(weekly_hold, args={"lookback" : look_back*4})
    featurizer.add_feature(daily_rolling_hold, args={"lookback" : look_back*30})
    return featurizer

def featurize(user_ids, gam_df, featurizer=None, features=None, look_forward=12):
    print("Starting frame making")
    if not featurizer:
        featurizer = make_default_featurizer(look_back=look_forward)
    #breakpoint()
    frames = [make_frame(user_id, gam_df, look_forward) 
                for user_id in user_ids]
    rgs = [demo_df.loc[user_id, 'rg'] == 1 
            for user_id in user_ids]
    return featurizer.vectorize(frames, features), rgs

def make_frame(user_id, gam_df, look_forward):
    mask = (gam_df['user_id'] == user_id)
    user_daily = gam_df[mask]
    first_deposit = demo_df.loc[user_id, 'first_deposit_date']
    user_frame = sparse_to_ts(user_daily, date_start=first_deposit, window=30*look_forward)
    return user_frame

def get_rg_date(user_id, demo_info, rg_df):
    rg_date = None
    if demo_info.loc[user_id, 'rg'] == 1:
        rg_date = rg_df.loc[user_id, 'first_date']
    return rg_date

if __name__ == '__main__':
    user_ids = [912480, 3789290, 5313473, 5296662]
    vector, rgs = featurize(user_ids, gam_df, features=["weekly_hold"])
    print(len(vector), len(rgs), len(vector[0]))