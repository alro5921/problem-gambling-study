import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import random

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

from featurizing import featurize
from Featurizer import Featurizer
from features import SUMMARY_NAMES, DAILY_NAMES, WEEKLY_NAMES

from pipeline import get_demo_df, get_gam_df, get_rg_df
from pipeline import sparse_to_ts

from preprocessing import filter_preprocess

RF_GRID = {'max_depth': [3, 5, None],
                'max_features': ['sqrt', 'log2', None],
                'min_samples_split': [2, 4, 8],
                'min_samples_leaf': [1, 5, 10, 20],
                'bootstrap': [True, False],
                'n_estimators': [50, 100, 200, 400],
                'random_state': [1]}

GRAD_BOOST_GRID = {'learning_rate': [0.01, 0.001, 0.0001],
                                'max_depth': [3, 5],
                                'min_samples_leaf': [5, 10, 50, 100, 200],
                                'max_features': [2, 3, 5, 10],
                                'n_estimators': [150, 300, 500],
                                'random_state': [1]}

GRAD_GS_GUESS = {'learning_rate': .001, 'n_estimators': 300, 
                'min_samples_leaf': 5, 'max_features': 5}

RF_GS_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 4, 
                    'min_samples_leaf': 1, 'max_features': 'sqrt', 'max_depth': None}

def preprocessing(months, user_ids=None, featurizer=None, features=None, prefilter=True, dfs=None):
    if not featurizer and not features:
        print("Need at least one way to get featurizing context!")
        raise ValueError
    if not dfs:
        demo_df = get_demo_df()
        rg_df = get_rg_df()
        gam_df = get_gam_df()
    else:
        demo_df, rg_df, gam_df = dfs
    if not user_ids:
        user_ids = list(demo_df.index)

    days = months * 30
    if(prefilter):
        print("Applying prefilters")
        user_ids = filter_preprocess(user_ids, months*30, demo_df, rg_df)
    print(f"Constructing model with {months} months of information")
    print(f"Features being used: {features}")
    X, y = featurize(user_ids, gam_df, featurizer=featurizer, features=features, month_window=months)
    return X, y, user_ids

def train(X, y, base_model, do_grid=True, grid=None, search_params=None, save=False, verbose=True):
    if not do_grid:
        print("Not doing a grid search, just using a prior model's hyperparameters.")
        regressor = RandomForestClassifier(**RF_GS_GUESS)
        regressor.fit(X, y)
        return regressor, None
    if not search_params:
        search_params = {'n_iter' : 100, 'n_jobs' : -1, 'cv' : 5}
    gridsearch = RandomizedSearchCV(base_model, grid, scoring='f1', verbose=verbose, **search_params)
    gridsearch.fit(X, y)
    
    regressor = gridsearch.best_estimator_
    if save:
        now = datetime.now().strftime("%m-%d-%H-%M")
        #name = base_model.__name__ 
        gs_path = f'model/grid_results{now}.pkl'
        with open(gs_path, 'wb') as f:
            pickle.dump(gridsearch, f)
        model_path = f'model/model{now}.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(regressor, f)
    print(f'Model CV Score: {gridsearch.best_score_:.3f}')
    return regressor, gridsearch
    
def predict(model, X, y=None, user_ids=None, store_name="", thres=.5, verbose=True, store=True):
    y_prob = model.predict_proba(X)[:,1]
    if store:
        val_store = pd.DataFrame({"prediction" : y_prob})
        if y:
            val_store["actual"] = y
        if user_ids:
            val_store["id"] = user_ids
        now = datetime.now()
        val_store.to_csv(f'data/model_results/{store_name}_prediction_results{now}.csv')
    if verbose and y:
        y_pred = (y_prob >= thres).astype(int)
        scores(y,y_pred)
    return y_prob

def scores(y_test,y_pred):
    confus = confusion_matrix(y_test,y_pred)
    tn, fp, fn, tp = confus.ravel()
    print(f'True Neg {tn}, False Pos {fp}, False Neg {fn}, True Positive {tp}')
    print(f'Accuracy: {accuracy_score(y_test,y_pred):.3f}')
    print(f'Recall: {recall_score(y_test, y_pred):.3f}')
    print(f'Precision: {precision_score(y_test,y_pred):.3f}')
    print(f'F1: {f1_score(y_test,y_pred):.3f}')

if __name__ == '__main__':
    months = 6
    features = SUMMARY_NAMES + ['weekly_hold', 'weekly_activity']
    X, y, user_ids = preprocessing(months, features = features)
    model, gs = train(X, y, RandomForestClassifier(), do_grid=True, grid=RF_GRID)
    #model, gs = train(X, y, GradientBoostingClassifier(), do_grid=True, grid=GRAD_BOOST_GRID)
    # Looks like weekly_hold + weekly_activity is doing well

    # SUMMARY_FEATURES = [total_hold, max_hold, total_activity, total_fixed_live_ratio, total_nonzero_hold_std]
    # DAILY_FEATURES = [daily_hold, daily_rolling_hold]
    # WEEKLY_FEATURES = [weekly_hold, weekly_activity, weekly_rolling_hold, weekly_rolling_activity, weekly_fixed_live_ratio]
    # ALL_FEATURES = SUMMARY_FEATURES + DAILY_FEATURES + WEEKLY_FEATURES

    # feat_combs = power_set(NON_DAILY)
    # print(f"Constructing model with {months} months of information")
    # for feats in feat_combs:

    run_holdout = False
    seriously = False
    if run_holdout and seriously:
        HOLD_DEMO_PATH = 'data/holdout/demographic.csv'
        HOLD_RG_PATH = 'data/holdout/rg_information.csv'
        HOLD_GAM_PATH = 'data/holdout/gambling.csv'
        hold_demo = get_demo_df(HOLD_DEMO_PATH)
        hold_rg = get_rg_df(HOLD_RG_PATH)
        hold_gam = get_gam_df(HOLD_GAM_PATH)
        dfs = [hold_demo, hold_rg, hold_gam]
        X, y, user_ids = preprocessing(months=months, features=features, dfs=dfs)
        predict(model, X, y, user_ids)