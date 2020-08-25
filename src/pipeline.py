import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import random
from pipeline_constants import (DEMO_RENAME, GAMBLING_RENAME, RG_RENAME, 
                            HAS_HOLD_DATA, EVENT_CODE_DICT, INTERVENTION_CODE_DICT)

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

def make_ts(gam_data, user_id, product_type, demographic_df = None):
    mask = (gam_data['user_id'] == user_id) & (gam_data['product_type'] == product_type)
    series = gam_data[mask].copy()
    if demographic_df:
        reg_date = demographic_df.loc[user_id].registration_date
    #last_gamble = series['date'].max()
    idx = pd.date_range(reg_date, '2010-11-30')
    series = series.set_index('date')
    series = series.reindex(idx, fill_value=0)
    series = series.replace({"user_id" : {0 : user_id}, "product_type": {0 : product_type}})
    #series['hold_cum'] = series['hold'].cumsum() #Move this out later
    return series

def accum_by_date(gam_data, user_id, product_types = HAS_HOLD_DATA, demographic_df = None):
    '''Accumulates the turnover+hold across all product_types'''
    mask = (gam_data['user_id'] == user_id) & (gam_data['product_type'].isin(product_types))
    series = gam_data[mask].groupby('date').sum()
    series = series.drop(["product_type","user_id"], axis = 1)
    min_date = demographic_df.loc[user_id].registration_date if demographic_df is not None else '2000-05-01'
    #last_gamble = series['date'].max()
    idx = pd.date_range(min_date, '2010-11-30')
    series = series.reindex(idx, fill_value=0)
    # series['weekend'] = pd.DatetimeIndex(series.index).dayofweek >= 4
    # series['hold_cum'] = series['hold'].cumsum() #Move this out later
    return series.copy()

def add_cumulative(series, col = 'hold', cum_name = None):
    if not name:
        name = col + '_cum'
    series[cum_name] = series[col].cumsum()
    return series

def add_weekend(series):
    series['weekend'] = pd.DatetimeIndex(series.index).dayofweek >= 4
    return series

def add_weighted_bets(gam_df, w_means = None):
    if not w_means:
        w_means = gam_df.groupby('product_type')['num_bets'].mean()
        w_means /= w_means[1]
    gam_df['weighted_bets'] = 0
    for product_type in gam_df['product_type'].unique():
        mask = gam_df['product_type'] == product_type
        gam_df.loc[mask,'weighted_bets'] = gam_df[mask]['num_bets'] / w_means[product_type]
    return gam_df

def gambling_pipeline(gam_path = 'data/raw_2.sas7bdat'):
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

def subset_rg(rg_info, events = None, interventions = None):
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

if __name__ == '__main__':
    pass