import numpy as np
import pandas as pd
import re
from datetime import datetime
import pipeline
from itertools import chain
from collections.abc import Iterable

# Global variables weeee
demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

class Featurizer:
    def __init__(self):
        self.features = {}

    def vectorize_user(self, user_data, choices='all'):
        vect = []
        for feat in self.features:
            if choices == 'all' or feat in choices:
                feat_val = self.features[feat](user_data)
                if isinstance(feat_val, Iterable):
                    vect += [*feat_val]
                else:
                    vect += [feat_val]
        return vect

    def add_feature(self, feat_name, prod_function, prod_args={}):
        self.features[feat_name] = lambda x: prod_function(x, **prod_args)

class FeatureCache:
    def __init__(self):
        self.featurizer = Featurizer()
        self.reg_features_path = 'data/featurized.csv'
        self.ts_features_path = []

    def get_feature(self, feat_name):
        df = pd.read_csv(self.reg_features_path)
        if feat_name in df:
            print("Feature already stored!")

def total_hold(set_ts):
    return set_ts['hold'].sum()

def max_hold(set_ts):
    return set_ts['hold'].max()

def total_activity(set_ts):
    return set_ts['weighted_bets'].sum()

def weekly_hold(set_ts, lookback=52):
    weekly_sum = set_ts.resample('W').sum()
    return weekly_sum['hold'].values[-lookback:]

if __name__ == "__main__":
    user_id = 3327778
    featurizer = Featurizer()
    featurizer.add_feature("total_hold", total_hold)
    featurizer.add_feature("max_hold", max_hold)
    featurizer.add_feature("total_activity", total_activity)
    featurizer.add_feature("weekly_hold", weekly_hold, {"lookback" : 26})

    gam_df = pipeline.gambling_pipeline()
    user_ts = pipeline.accum_by_date(gam_df, user_id)
    features_to_use = ["total_hold", "max_hold", "weekly_hold"]
    x = featurizer.vectorize_user(user_ts, features_to_use)
    print(len(x))