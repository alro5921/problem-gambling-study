import numpy as np
import pandas as pd
import random
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

    def vectorize(self, frames, choices=None):
        if not choices:
            choices = self.get_feature_names()
        return np.array([self.vectorize_frame(frame, choices) for frame in frames])

    def vectorize_frame(self, frame, choices=None):
        vect = []
        #breakpoint()
        if not choices:
            choices = self.get_feature_names()
        for feat in choices:
            feat_val = self.features[feat](frame)
            if isinstance(feat_val, Iterable):
                vect += [*feat_val]
            else:
                vect += [feat_val]
        return vect

    def _calc_feature(self, frame, feat_name):
        return self.features[feat](frame)

    def add_feature(self, feat_name, prod_function, prod_args={}):
        self.features[feat_name] = lambda x: prod_function(x, **prod_args)

    def delete_feature(self, feat_name):
        del self.features[feat_name]

    def get_feature_names(self):
        return list(self.features.keys())

# import pickle

# class FeatureCache:
#     def __init__(self, store_path=None):
#         self.featurizer = Featurizer()
#         self.store_path = store_path if store_path else 'data/featurized.pkl'
#         self.cache = pd.DataFrame()

#     def _load_csv(self):
#         try:
#             self.cache = pickle.load(open(self.store_path,'rb'))
#         except FileNotFoundError:
#             print(f"No pkl cache found at {self.store_path}, making its own")
#             pickle.dump(self.cache, open(self.store_path, 'wb'))

#     def store(self):
#         pickle.dump(self.cache, open(self.store_path, 'wb'))

#     def add_feature(self, feat_name, prod_function, prod_args = {}, overwrite=True):
#         if not overwrite and feat_name in self.features:
#             return
#         raw_ts = self.cache['raw_ts']
#         self.cache[feat_name] = [prod_function(row, **prod_args) for row in raw_ts]

#     def vectorize(self, features=None): 
#         if not features:
#             features = self.get_feature_names()

#     def get_feature_names(self):
#         return self.featurizer.get_feature_names()

#     # def set_df(self, feature_name, overwrite = False):
#     #     X = 
#     #     df[feature_name] = self.featurizer.calc_feature(feature_name, user)

if __name__ == "__main__":
    user_id = 3327778

    def total_hold(set_ts):
        return set_ts['hold'].sum()

    def max_hold(set_ts):
        return set_ts['hold'].max()

    def weekly_hold(set_ts, lookback=52):
        weekly_sum = set_ts.resample('W').sum()
        return weekly_sum['hold'].values[-lookback:]

    def rolling_hold(set_ts, lookback=52):
        weekly_sum = set_ts.resample('W').sum()
        return weekly_sum['weighted_bets'].rolling(5).sum()[4:]

    featurizer = Featurizer()
    featurizer.add_feature("total_hold", total_hold)
    featurizer.add_feature("max_hold", max_hold)
    featurizer.add_feature("rolling_hold", rolling_hold)
    featurizer.add_feature("weekly_hold", weekly_hold, {"lookback" : 26})

    gam_df = pipeline.gambling_pipeline()
    user_ts = pipeline.accum_by_date(gam_df, user_id)
    features_to_use = ["total_hold", "max_hold", "weekly_hold"]
    x = featurizer.vectorize_user(user_ts, features_to_use)
    print(len(x))
    print(x[:30])