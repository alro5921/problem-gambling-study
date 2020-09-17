import numpy as np
import pandas as pd
from datetime import datetime
import random

# def filter_low_activity(user_ids, gam_df, activity=20):
#     filt_users = []
#     for user_id in user_ids:
#         mask = (gam_df['user_id'] == user_id)
#         user_daily = gam_df[mask]
#         if user_daily['weighted_bets'].sum() > activity:
#             filt_users.append(user_id)
#     return filt_users

def filter_rg_in_frame(users_ids, days_ahead, demo_df, rg_df):
    print("Filtering out RGs with event in frame")
    df = demo_df.join(rg_df)
    df['registration_date'] = pd.to_datetime(df['registration_date'])
    df['first_date'] = pd.to_datetime(df['first_date'])
    df['diff'] = df['first_date'] - df['registration_date']
    mask = (df['rg'] == 1) & (df['diff'] < np.timedelta64(days_ahead, 'D'))
    return list(df[~mask].index)

def sample_adjust(user_ids, demo_df):
    '''Balances the sample while preserving all RG events,
    i.e over/undersample the non-RG users as needed
    '''
    print("Rebalancing classes")
    demo_filt = demo_df[demo_df.index.isin(user_ids)]
    rg_ids = list(demo_filt[demo_filt['rg'] == 1].index)
    no_rg_ids = list(demo_filt[demo_filt['rg'] == 0].index)
    diff = len(rg_ids) - len(no_rg_ids)
    if diff > 0:
        print("Oversampling")
        no_rg_ids = no_rg_ids + random.sample(no_rg_ids, k=diff)
    else:
        print("Undersampling")
        no_rg_ids = random.choices(no_rg_ids, k=len(rg_ids))
    return rg_ids + no_rg_ids

def filter_preprocess(user_ids, days_ahead, demo_df, rg_df):
    user_ids = filter_rg_in_frame(user_ids, days_ahead, demo_df, rg_df)
    user_ids = sample_adjust(user_ids, demo_df)
    return user_ids
