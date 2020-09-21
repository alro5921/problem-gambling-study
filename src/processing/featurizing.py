import numpy as np
import pandas as pd
from datetime import datetime
from .Featurizer import Featurizer
from .features import (SUMMARY_FEATURES,ALL_FEATURES)
from pipeline import get_demo_df, get_gam_df, get_rg_df 
from pipeline import sparse_to_ts

def make_default_featurizer():
    featurizer = Featurizer()
    for feature in ALL_FEATURES:
        featurizer.add_feature(feature)
    return featurizer

def featurize(user_ids, gam_df, demo_df, featurizer=None, features=None, month_window=12):
    print("Starting frame making")
    if not featurizer:
        featurizer = make_default_featurizer()
    frames = [make_frame(user_id, gam_df, demo_df, month_window) 
                for user_id in user_ids]
    rgs = [demo_df.loc[user_id, 'rg'] == 1 
            for user_id in user_ids]
    return featurizer.vectorize(frames, features), rgs

def make_frame(user_id, gam_df, demo_df, month_window):
    mask = (gam_df['user_id'] == user_id)
    user_daily = gam_df[mask]
    first_deposit = demo_df.loc[user_id, 'first_deposit_date']
    user_frame = sparse_to_ts(user_daily, date_start=first_deposit, window=30*month_window)
    return user_frame

if __name__ == '__main__':
    demo_df = get_demo_df()
    gam_df = get_gam_df()
    rg_df = get_rg_df()
    user_ids = list(demo_df.index)
    print(len(user_ids))
    #print(len(filter_rg_in_frame(user_ids, 180)))