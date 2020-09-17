import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import random

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
#from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

from processing.featurizing import featurize
from processing.Featurizer import Featurizer
from processing.features import SUMMARY_NAMES, DAILY_NAMES, WEEKLY_NAMES

from pipeline import get_demo_df, get_gam_df, get_rg_df
from processing.preprocessing import filter_preprocess

from model_constants import *

def preprocessing(months, user_ids=None, featurizer=None, features=None, prefilter=True, dfs=None):
    '''Entire pipeline from the raw data to the numpy matrices needed for random forests'''
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
        user_ids = filter_preprocess(user_ids, months*30, demo_df, rg_df)
    print(f"Constructing model with {months} months of information")
    print(f"Features being used: {features}")
    X, y = featurize(user_ids, gam_df, demo_df, featurizer=featurizer, features=features, month_window=months)
    return X, y, user_ids

def train(X, y, base_model, do_grid=True, grid=None, search_params=None, save=False, verbose=True):
    if not do_grid:
        print("Not doing a grid search, just using a prior model's hyperparameters.")
        regressor = base_model()
        regressor.fit(X, y)
        return regressor, None
    if not search_params:
        search_params = {'n_iter' : 100, 'n_jobs' : -1, 'cv' : 5}
    gridsearch = RandomizedSearchCV(base_model, grid, scoring='f1', verbose=verbose, **search_params)
    gridsearch.fit(X, y)

    regressor = gridsearch.best_estimator_
    if save:
        now = datetime.now().strftime("%m-%d-%H-%M")
        gs_path = f'model/grid_results_{now}.pkl'
        with open(gs_path, 'wb') as f:
            pickle.dump(gridsearch, f)
        model_path = f'model/model_{now}.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(regressor, f)
    print(f'Model Av F1 Score: {gridsearch.best_score_:.3f}')
    return regressor, gridsearch
    
def predict(model, X, y=None, user_ids=None, store=True, store_name="", thres=.5, verbose=True):
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
    train_model = True
    features = SUMMARY_NAMES + ['weekly_hold', 'weekly_activity', 'weekly_max']
    if train_model:
        X, y, user_ids = preprocessing(months, features=features)
        model, gs = train(X, y, RandomForestClassifier(), do_grid=True, grid=RF_GRID, save=True)
        df = pd.DataFrame(gs.cv_results_)

    run_holdout = False
    seriously = False
    if run_holdout and seriously:
        print("!!!!Running on holdout!!!!")
        HOLD_DEMO_PATH = 'data/holdout/demographic.csv'
        HOLD_RG_PATH = 'data/holdout/rg_information.csv'
        HOLD_GAM_PATH = 'data/holdout/gambling.csv'
        hold_demo = get_demo_df(HOLD_DEMO_PATH)
        hold_rg = get_rg_df(HOLD_RG_PATH)
        hold_gam = get_gam_df(HOLD_GAM_PATH)
        dfs = [hold_demo, hold_rg, hold_gam]
        X, y, user_ids = preprocessing(months=months, features=features, dfs=dfs)
        predict(model, X, y, user_ids, store=False)
