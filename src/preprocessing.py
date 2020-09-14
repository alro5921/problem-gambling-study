import numpy as np
import pandas as pd
import re
import random
from sklearn.model_selection import train_test_split
from pipeline_constants import (DEMO_RENAME, GAMBLING_RENAME, RG_RENAME, ALL_PRODUCTS, 
                            HAS_HOLD_DATA, EVENT_CODE_DICT, INTERVENTION_CODE_DICT)


'''A one time run that cleans and formats the initial raw data, then creates a train/holdout set''' 

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

def create_demo_df(demo_path = 'data/raw/raw_1.sas7bdat'):
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

def create_rg_df(rg_path = 'data/raw/raw_3.sas7bdat'):
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

def to_daily(gam_df, product_types = ALL_PRODUCTS):
    '''Converts the (date sparse) [user,product,date] DF into a (date sparse) [user,date] DF,
    creating new columns to mantain specific product info as desired in product_types.
    '''
    for product in product_types:
        if product in HAS_HOLD_DATA:
            prod_cols = ['turnover', 'hold', 'num_bets']
        else:
            prod_cols = ['num_bets']
        new_cols = [col + f'_{product}' for col in prod_cols]
        for new_col in new_cols:
            gam_df[new_col] = 0 # Surprised you can't do this all at once
        prod_mask = gam_df["product_type"] == product
        gam_df.loc[prod_mask, new_cols] = gam_df.loc[prod_mask, prod_cols].values

    gb_user_date = gam_df.groupby(['user_id', 'date']).sum()
    gb_user_date.drop("product_type", inplace=True, axis = 1)
    # Currently returning as a flattened thing for legacy sake, but maybe should keep as a multiindex? Hmm.
    return gb_user_date.reset_index(drop=False)

def create_gam_df(gam_path='data/raw/raw_2.sas7bdat'):
    df = pd.read_sas(gam_path)
    df = clean_gambling(df)
    df = to_daily(df)
    return df

def subset_users(user_ids, df):
    return df[df.index.isin(user_ids)]

def create_holdout(demo_df, gam_df, rg_df, random_state=104, test_size=.15):
    '''Running this once to create a holdout set'''
    user_ids = list(demo_df.index)
    train_ids, holdout_ids = train_test_split(user_ids, 
                                    random_state=random_state, test_size = test_size)
    train_demo, test_demo = subset_users(train_ids, demo_df), subset_users(holdout_ids, demo_df)
    train_gam = gam_df[gam_df['user_id'].isin(train_ids)]
    test_gam = gam_df[gam_df['user_id'].isin(holdout_ids)] 
    train_rg, test_rg = subset_users(train_ids, rg_df), subset_users(holdout_ids, rg_df)
    train_demo.to_csv(f'data/demographic.csv', orient='table')
    train_gam.to_csv(f'data/gambling.csv')
    train_rg.to_csv(f'data/rg_information.csv')
    test_demo.to_csv(f'data/holdout/demographic.csv')
    test_gam.to_csv(f'data/holdout/gambling.csv')
    test_rg.to_csv(f'data/holdout/rg_information.csv')

def init():
    demo_df = create_demo_df()
    gam_df = create_gam_df()
    rg_df = create_rg_df()
    create_holdout(demo_df, gam_df, rg_df)

if __name__ == '__main__':
    init()
    #gam_df = create_gam_df()
    #print(gam_df.head(), gam_df.tail())
