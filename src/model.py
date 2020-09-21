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
    '''Entire pipeline from the raw data to the numpy matrices needed for sklearn... learners'''
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
        print("Not doing a grid search, just using a base model.")
        regressor = base_model()
        regressor.fit(X, y)
        return regressor, None
    if not search_params:
        search_params = DEFAULT_GRID_PARAMS
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
    feature_sets = [SUMMARY_NAMES[:4] + ['weekly_hold', 'weekly_activity']]
    for features in feature_sets:
        X, y, user_ids = preprocessing(months, features=features)
        X_train, X_test, y_train, y_test, user_train, user_test = train_test_split(X, y, user_ids)
        model, gs = train(X_train, y_train, RandomForestClassifier(), do_grid=True, grid=RF_GRID, save=True)
        predict(model, X_test, y_test, user_test, store_name="ROC")
    #     #df = pd.DataFrame(gs.cv_results_)
    # X, y, user_ids = preprocessing(months, features=SUMMARY_NAMES)
    # model, gs = train(X, y, RandomForestClassifier(), do_grid=True, grid=RF_GRID, save=True)
    # print(model.feature_importances_)
    # [0.23369659 0.15424682 0.24062864 0.29024191 0.07436665 0.00681938]