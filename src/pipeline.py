import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import random

DEMO_RENAME = {"USERID": "user_id", "RG_case" : "rg", "CountryName" : "country",
              "LanguageName" : "language", "Gender" : "gender", "YearofBirth" : "birth_year",
              "Registration_date" : "registration_date", "First_Deposit_Date" : "first_deposit_date"}

GAMBLING_RENAME = {"UserID": "user_id", "Date" : "date", "ProductType" : "product_type",
              "Turnover" : "turnover", "Hold" : "hold", "NumberofBets" : "num_bets"}

RG_RENAME = {"UserID": "user_id", "RGsumevents" : "events", "RGFirst_Date" : "first_date", 
             "Event_type_first" : "event_type_first", 
             "RGLast_date" : "last_date", "Interventiontype_first" : "inter_type_first"}

HAS_HOLD_DATA = [1,2,4,8,17]

EVENT_CODE_DICT = {1: "Family Intervention", 2 : "acc close/open from RG", 3 : "Cancelled outpayment", 
                   4: "Manual (Lower?) Limit Change", 6: "Heavy Complainer", 7: "Requested pay method block",
                   8: "Reported as Minor", 9: "Request partial block", 10: "Reported Problem", 
                   11: "high deposit", 12 : "Two RG events on the day", 13: "Event unknown"}

INTERVENTION_CODE_DICT = {-1: "Intevention Unknown", 1: "Advice", 2: "Reopen", 
                          3: "Consumer request not technically possible", 4: "Block (pending invest)",
                          5: "VIP Deposit Change", 6: "Partial Block (incomplete)", 7: "Advice To 3rd Party",
                          8: "Partial Block", 9: "Inpayment not blocked", 10 : "Inpayment blocked",
                          11: "Higher deposit denied", 12 : "Higher Deposit Accepted", 13 : "Daily/weekly deposit changed", 
                          14: "Full Block", 15 : "Betting Limit Change", 16: "Remains Blocked", 
                          17 : "Blocked and Reimbursed", 18: "Requested Partial Block Not Possible"}

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
    clean_df = clean_df.fillna({'registration_date' : pd.to_datetime('1900-01-01'), 'birth_year' : 1900})
    clean_df[['user_id', 'rg', 'birth_year']] = clean_df[['user_id', 'rg', 'birth_year']].astype(int)
    obj_rows = ['country','language','gender']
    for obj in obj_rows:
        clean_df[obj] = clean_str_series(clean_df[obj])
    clean_df.set_index('user_id', inplace = True)
    return clean_df

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
    series['hold_cum'] = series['hold'].cumsum() #Move this out later
    return series

def accum_by_date(gam_data, user_id, product_types = HAS_HOLD_DATA, demographic_df = None):
    '''Accumulates the turnover+hold across all product_types'''
    mask = (gam_data['user_id'] == user_id) & (gam_data['product_type'].isin(product_types))
    series = gam_data[mask].groupby('date').sum()
    series = series.drop(["product_type","user_id"], axis = 1)
    if demographic_df:
        reg_date = demographic_df.loc[user_id].registration_date
    #last_gamble = series['date'].max()
    idx = pd.date_range(reg_date, '2010-11-30')
    series = series.reindex(idx, fill_value=0)
    series['hold_cum'] = series['hold'].cumsum() #Move this out later
    return series.copy()

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

if __name__ == '__main__':
    pass