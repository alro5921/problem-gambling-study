import numpy as np
import pandas as pd
from datetime import datetime
import random
from .featurizing import featurize
from pipeline import get_demo_df, get_gam_df, get_rg_df

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
        print("Oversampling No-RGS")
        no_rg_ids = no_rg_ids + random.sample(no_rg_ids, k=diff)
    else:
        print("Undersampling No-RGS")
        no_rg_ids = random.choices(no_rg_ids, k=len(rg_ids))
    return rg_ids + no_rg_ids

def prefilters(user_ids, days_ahead, demo_df, rg_df):
    user_ids = filter_rg_in_frame(user_ids, days_ahead, demo_df, rg_df)
    user_ids = sample_adjust(user_ids, demo_df)
    return user_ids

def preprocessing(months, user_ids=None, featurizer=None, features=None, prefilter=True, dfs=None):
    '''Entire pipeline from the raw data to the numpy matrices needed for sklearn... learners'''
    if not featurizer and not features:
        print("Need at least one way to get featurizing context!")
        raise ValueError
    if not dfs:
        demo_df, rg_df, gam_df = get_demo_df(), get_rg_df(), get_gam_df()
    else:
        demo_df, rg_df, gam_df = dfs
    if not user_ids:
        user_ids = list(demo_df.index)

    days = months * 30
    if(prefilter):
        print("Applying prefilters")
        user_ids = prefilters(user_ids, months*30, demo_df, rg_df)
    print(f"Constructing model with {months} months of information")
    print(f"Features being used: {features}")
    X, y = featurize(user_ids, gam_df, demo_df, featurizer=featurizer, features=features, month_window=months)
    return X, y, user_ids