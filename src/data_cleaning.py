'''The initial processing from the raw data into the analytic form'''
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

def create_demo_df(demo_path = 'data/raw_1.sas7bdat'):
    df = pd.read_sas(demo_path)
    df = clean_demographic(df)
    return df

'''RG INFO'''

def clean_rg_info(rg_info):
    rg_info = rg_info.rename(RG_RENAME, axis = 1)
    int_cols = ['event_type_first', 'events', 'user_id']
    rg_info[int_cols] = rg_info[int_cols].astype(int)
    rg_info.set_index('user_id', inplace = True)
    rg_info['inter_type_first'] = rg_info['inter_type_first'].fillna(-1).astype(int)
    rg_info['ev_desc'] = rg_info['event_type_first'].replace(EVENT_CODE_DICT)
    rg_info['inter_desc'] = rg_info['inter_type_first'].replace(INTERVENTION_CODE_DICT)
    return rg_info

def create_rg_df(rg_path = 'data/raw_3.sas7bdat'):
    df = pd.read_sas(rg_path)
    df = clean_rg_info(df)
    return df

'''GAMBLING'''
def clean_gambling(gam_df):
    gam_clean = gam_df.copy()
    gam_clean = gam_clean.rename(GAMBLING_RENAME, axis = 1)
    gam_clean['num_bets'] = gam_clean['num_bets'].fillna(0)
    int_rows = ['user_id','product_type','num_bets']
    gam_clean[int_rows] = gam_clean[int_rows].astype(int)
    return gam_clean

def add_weighted_bets(gam_df, w_means=None):
    if not w_means:
        w_means = gam_df.groupby('product_type')['num_bets'].mean()
        w_means /= w_means[1]
    gam_df['weighted_bets'] = 0
    for product_type in gam_df['product_type'].unique():
        mask = gam_df['product_type'] == product_type
        gam_df.loc[mask,'weighted_bets'] = gam_df[mask]['num_bets'] / w_means[product_type]
    return gam_df

def to_daily(gam_df, product_types = HAS_HOLD_DATA, demographic_df=None):
    '''Converts a (date sparse) [user,product,date] DF into a (date sparse) [user,date] DF,
    creating new columns to mantain specific product info as desired in product_types.
    '''
    for product in product_types:
        if product in HAS_HOLD_DATA:
            prod_cols = ['turnover', 'hold', 'num_bets']
        else:
            prod_cols = ['num_bets']
        new_cols = [col + f'_{product}' for col in prod_cols]
        for new_col in new_cols:
            gam_df[new_col] = 0
        prod_mask = gam_df["product_type"] == product
        gam_df.loc[prod_mask, new_cols] = gam_df.loc[prod_mask, prod_cols].values
    gb_user_date = gam_df.groupby(['user_id', 'date']).sum()
    gb_user_date.drop("product_type", inplace=True, axis = 1)
    # Currently returning as a flattened thing for legacy sake, but should possibly keep as a multiindex? Hmm.
    return gb_user_date.reset_index(drop=False)

def create_gam_df(gam_path='data/raw_2.sas7bdat'):
    df = pd.read_sas(gam_path)
    df = clean_gambling(df)
    df = add_weighted_bets(df)
    products = [1,2,4,8,10,17]
    df = to_daily(df,products)
    return df

def sparse_to_ts(user_daily, date_start, date_end):
    

if __name__ == "__main__":
    df = create_gam_df()
    print(df.head())
