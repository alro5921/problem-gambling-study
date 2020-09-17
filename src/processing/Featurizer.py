import numpy as np
import pandas as pd
import random
import re
from datetime import datetime
import pipeline
from itertools import chain
from collections.abc import Iterable
from sklearn.preprocessing import scale
from .features import total_hold, max_hold, weekly_hold, weekly_rolling_hold

class Featurizer:
    def __init__(self):
        self.features = {}

    def vectorize(self, frames, choices=None, verbose=False):
        if not choices:
            choices = self.get_feature_names()
        if verbose:
            print(f"Making set with features: {', '.join(choices)}")
        X = np.array([self.vectorize_frame(frame, choices) for frame in frames])
        return X

    def vectorize_frame(self, frame, choices=None):
        vect = []
        if not choices:
            choices = self.get_feature_names()
        for feat in choices:
            feat_val = self.features[feat](frame)
            if isinstance(feat_val, Iterable):
                vect += [*feat_val]
            else:
                vect += [feat_val]
        return vect

    def add_feature(self, prod_function, feat_name=None, args={}):
        if not feat_name:
            feat_name = prod_function.__name__
        self.features[feat_name] = lambda x: prod_function(x, **args)

    def delete_feature(self, feat_name):
        del self.features[feat_name]

    def get_feature_names(self):
        return list(self.features.keys())

if __name__ == "__main__":
    demo_df = pipeline.get_demo_df()
    gam_df = pipeline.get_gam_df()
    rg_info = pipeline.get_rg_df()
    user_id = 3327778

    featurizer = Featurizer()
    featurizer.add_feature(total_hold)
    featurizer.add_feature(max_hold)
    featurizer.add_feature(weekly_hold)
    featurizer.add_feature(weekly_rolling_hold)

    mask = (gam_df['user_id'] == user_id)
    user_daily = daily_gam_df[mask]
    first_deposit = demo_df.loc[user_id, 'first_deposit_date']
    user_frame = sparse_to_ts(user_daily, date_start=first_deposit, window=180)
    features_to_use = ["total_hold", "max_hold", "weekly_hold"]
    x = featurizer.vectorize_frame(user_ts, user_frame)
    print(len(x))
    print(x[:30])