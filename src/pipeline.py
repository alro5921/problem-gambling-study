import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import random
import pickle
from pipeline_constants import (DEMO_RENAME, GAMBLING_RENAME, RG_RENAME, 
                            HAS_HOLD_DATA, EVENT_CODE_DICT, INTERVENTION_CODE_DICT)
from sklearn.model_selection import train_test_split
'''DEMOGRAPHIC'''

def clean_str_series(obj_ser):
    rep = lambda m: m.group(1)
    clean_ser = obj_ser.astype(str)
    clean_ser = (clean_ser.str.replace(pat = r"b\'(.*?)\'", repl = rep) #remove the b'*' structure
                            .str.lower()
                            .str.replace(pat = r"(.*?)\..*", repl = rep) #remove TLD if there
                            .replace(" ", "_", regex = True))
    clean_ser = clean_ser.replace("", "unknown")
    return clean_ser

def clean_demographic(df_demo):
    clean_df = df_demo.copy()
    clean_df = clean_df.rename(DEMO_RENAME, axis = 1)
    clean_df = clean_df.fillna({'registration_date' : pd.to_datetime('2006-01-01'), 'birth_year' : 1977})
    clean_df[['user_id', 'rg', 'birth_year']] = clean_df[['user_id', 'rg', 'birth_year']].astype(int)
    obj_rows = ['country','language','gender']
    for obj in obj_rows:
        clean_df[obj] = clean_str_series(clean_df[obj])
    clean_df.set_index('user_id', inplace = True)
    return clean_df

def demo_pipeline(demo_path = 'data/raw_1.sas7bdat'):
    df = pd.read_sas(demo_path)
    return clean_demographic(df)

'''GAMBLING'''
def clean_gambling(gam_df):
    gam_clean = gam_df.copy()
    gam_clean = gam_clean.rename(GAMBLING_RENAME, axis = 1)
    gam_clean['num_bets'] = gam_clean['num_bets'].fillna(0)
    int_rows = ['user_id','product_type','num_bets']
    gam_clean[int_rows] = gam_clean[int_rows].astype(int)
    return gam_clean

def user_product_ts(gam_df, user_id, product_type, demographic_df = None):
    mask = (gam_df['user_id'] == user_id) & (gam_df['product_type'] == product_type)
    user_ts = gam_df[mask].copy()
    reg_date = '2000-05-01'
    if demographic_df:
        reg_date = demographic_df.loc[user_id].registration_date
    idx = pd.date_range(reg_date, '2010-11-30')
    user_ts = user_ts.set_index('date')
    user_ts = user_ts[~user_ts.index.duplicated(keep='first')]
    user_ts = user_ts.reindex(idx, fill_value=0)
    user_ts = user_ts.replace({"user_id" : {0 : user_id}, "product_type": {0 : product_type}})
    return user_ts

def add_weighted_bets(gam_df, w_means=None):
    if not w_means:
        w_means = gam_df.groupby('product_type')['num_bets'].mean()
        w_means /= w_means[1]
    gam_df['weighted_bets'] = 0
    for product_type in gam_df['product_type'].unique():
        mask = gam_df['product_type'] == product_type
        gam_df.loc[mask,'weighted_bets'] = gam_df[mask]['num_bets'] / w_means[product_type]
    return gam_df

def to_daily_ts(gam_df, user_id, product_types = HAS_HOLD_DATA, demographic_df=None):
    '''Accumulates the turnover+hold across all product_types'''
    mask = (gam_df['user_id'] == user_id) #& (gam_df['product_type'].isin(product_types))
    user_ts = gam_df[mask].groupby('date').sum()

    # Creating product specific columns
    prod_dict = {product : user_product_ts(gam_df, user_id, product) 
                    for product in product_types}
    for prod, prod_df in prod_dict.items():
        prod_cols = ['turnover', 'hold', 'num_bets']
        user_ts = user_ts.join(prod_df[prod_cols], rsuffix = f'_{prod}')
    user_ts = user_ts.fillna(0)

    min_date = demographic_df.loc[user_id].registration_date if demographic_df is not None else '2000-05-01'
    user_ts = user_ts.drop(["product_type"], axis = 1)
    idx = pd.date_range(min_date, '2010-11-30')
    user_ts = user_ts.reindex(idx, fill_value=0)
    return user_ts.copy()

def add_weekend(series):
    series['weekend'] = pd.DatetimeIndex(series.index).dayofweek >= 4
    return series

def gambling_pipeline(gam_path='data/raw_2.sas7bdat'):
    df = pd.read_sas(gam_path)
    df = clean_gambling(df)
    df = add_weighted_bets(df)
    return df

'''RG'''
def clean_rg_info(rg_info):
    rg_info = rg_info.rename(RG_RENAME, axis = 1)
    int_cols = ['event_type_first', 'events', 'user_id']
    rg_info[int_cols] = rg_info[int_cols].astype(int)
    rg_info.set_index('user_id', inplace = True)
    rg_info['inter_type_first'] = rg_info['inter_type_first'].fillna(-1).astype(int)
    rg_info['ev_desc'] = rg_info['event_type_first'].replace(EVENT_CODE_DICT)
    rg_info['inter_desc'] = rg_info['inter_type_first'].replace(INTERVENTION_CODE_DICT)
    return rg_info

def subset_rg(rg_info, events=None, interventions=None):
    filtered_rg = rg_info.copy()
    if events:
        event_mask = filtered_rg['event_type_first'].isin(events)
        filtered_rg  = filtered_rg[event_mask]
    if interventions:
        intervent_mask = filtered_rg['inter_type_first'].isin(interventions)
        filtered_rg  = filtered_rg[intervent_mask]
    return filtered_rg

def rg_pipeline(rg_path = 'data/raw_3.sas7bdat'):
    df = pd.read_sas(rg_path)
    df = clean_rg_info(df)
    return df

def user_ts_dict(user_ids, gam_df=None, product_types=HAS_HOLD_DATA):
    if gam_df is None:
        gam_df = gambling_pipeline()
    user_dict = {}
    for user_id in user_ids:
        user_dict[user_id] = to_daily_ts(gam_df, user_id, product_types=product_types)
    return user_dict

def filter_appeals(users, rg_df=None):
    if rg_df is None:
        rg_df = rg_pipeline()
    appeals = rg_df['event_type_first'] == 2
    return rg_df[~appeals].index

def filter_low_activity(user_info, gam_df=None, activity_thres=50):
    if not isinstance(user_info, dict):
        user_info = user_ts_dict(users, gam_df)
    if gam_df is None:
        gam_df = gambling_pipeline()
    user_list = []
    for user, df in user_info.items():
        act = df['weighted_bets'].sum()
        if (act > activity_thres):
            user_list.append(user)
    return user_list

def filter_users(users, gam_df=None, rg_df=None):
    users = filter_appeals(users, rg_df)
    users = filter_low_activity(users, gam_df)
    return users

if __name__ == '__main__':
    demo_df = demo_pipeline()
    gam_df = gambling_pipeline()
    rg_df = rg_pipeline()
    # user_id = 912480
    # use_df = to_daily_ts(gam_df, user_id, demographic_df=demo_df)
    # # print(use_df.head())
    # # print(use_df.columns)
    user_ids = list(demo_df.index)
    user_ids = filter_appeals(user_ids, rg_df)
    user_ids = filter_low_activity(user_ids)
    user_dict = user_ts_dict(user_ids[:10], gam_df)
    path = 'data/user_id_test.pkl'
    pickle.dump(user_dict, open(path, 'wb'))
    dict_2 = pickle.load(open(path,'rb'))
    for id, df in dict_2.items():
        print(id)
        print(df[['hold', 'weighted_bets']].sum())
