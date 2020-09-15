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
from features import SUMMARY_NAMES, WEEKLY_NAMES

from pipeline import get_demo_df, get_gam_df, get_rg_df
from pipeline import sparse_to_ts

demo_df = get_demo_df()
rg_df = get_rg_df()

def train_grad_boost(X_train, y_train, do_grid=False):
    grad_boost_grid = {'learning_rate': [0.01, 0.001, 0.0001],
                                'max_depth': [3, 5],
                                'min_samples_leaf': [5, 10, 50, 100, 200],
                                'max_features': [2, 3, 5, 10],
                                'n_estimators': [150, 300, 500],
                                'random_state': [1]}
    gb_gridsearch = RandomizedSearchCV(GradientBoostingClassifier(),
                                grad_boost_grid,
                                n_iter = 400,
                                n_jobs=-1,
                                verbose=True,
                                scoring='f1')
    gb_gridsearch.fit(X_train, y_train)
    print("GB RGS parameters:", gb_gridsearch.best_params_)
    regressor = gb_gridsearch.best_estimator_
    return regressor

def train_baseline(X_train,y_train, do_grid=True):
    log_model = LogisticRegression(max_iter=500)
    log_model.fit(X_train, y_train)
    return log_model

GRID_SEARCH_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 2,
                     'min_samples_leaf': 5, 'max_features': None, 'max_depth': None, 'bootstrap': True}

LOOKFORWARD_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 4, 
                    'min_samples_leaf': 1, 'max_features': 'sqrt', 'max_depth': None, 'bootstrap': False}

def train_random_forest(X_train, y_train, do_grid=False, save=False):
    '''Trains a random forest model on the training frames, doing grid_search if needed'''
    if not do_grid:
        print("Not doing grid search, just using a prior model's GS")
        regressor = RandomForestClassifier(**GRID_SEARCH_GUESS)
        regressor.fit(X_train, y_train)
        return regressor
    random_forest_grid = {'max_depth': [3, 5, None],
                        'max_features': ['sqrt', 'log2', None],
                        'min_samples_split': [2, 4, 8],
                        'min_samples_leaf': [1, 5, 10, 20],
                        'bootstrap': [True, False],
                        'n_estimators': [50, 100, 200],
                        'random_state': [1]}
    rf_gridsearch = RandomizedSearchCV(RandomForestClassifier(),
                                random_forest_grid,
                                n_iter = 200,
                                n_jobs=-1,
                                verbose=True,
                                scoring='f1',
                                cv=3)
    rf_gridsearch.fit(X_train, y_train)
    if save:
        now = datetime.now().strftime("%m-%d-%H:%M")
        gs_path = f'model/rf_rgrid_output_{now}.pkl'
        with open(gs_path, 'wb') as f:
            pickle.dump(rf_gridsearch, f)
    #print("Random Forest RGS parameters:", rf_gridsearch.best_params_)
    regressor = rf_gridsearch.best_estimator_
    #print(regressor.feature_importances_)
    return regressor

def scores(y_test,y_pred):
    confus = confusion_matrix(y_test,y_pred)
    tn, fp, fn, tp = confus.ravel()
    print(f'True Neg {tn}, False Pos {fp}, False Neg {fn}, True Positive {tp}')
    print(f'Accuracy: {accuracy_score(y_test,y_pred):03}')
    print(f'Recall: {recall_score(y_test, y_pred):03}')
    print(f'Precision: {precision_score(y_test,y_pred):03}')
    print(f'F1: {f1_score(y_test,y_pred):03}')

def predict_and_store(model, user_ids, X_test, y_test, store_name="", verbose=True, thres=.5):
    y_prob = model.predict_proba(X_test)[:,1]
    val_store = pd.DataFrame({"id": user_ids, "actual" : y_test, "prediction" : y_prob})
    now = datetime.now()
    val_store.to_csv(f'data/model_results/{store_name}_prediction_results{now}.csv')

    y_pred = (y_prob >= thres).astype(int)
    if verbose:
        scores(y_test,y_pred)
    return y_prob

def filter_low_activity(user_ids, activity=20):
    filt_users = []
    for user_id in user_ids:
        mask = (gam_df['user_id'] == user_id)
        user_daily = gam_df[mask]
        if user_daily['weighted_bets'].sum() > activity:
            filt_users.append(user_id)
    return filt_users

def filter_users(user_ids, demo_df, gam_df):
    print("Filtering low activity")
    ids = filter_low_activity(user_ids)
    demo_filt = demo_df[demo_df.index.isin(ids)]
    rg_ids = list(demo_filt[demo_filt['rg'] == 1].index)
    no_rg_ids = list(demo_filt[demo_filt['rg'] == 0].index)
    print("Rebalancing classes with oversampling")
    user_ids = rg_ids + random.choices(no_rg_ids, k=len(rg_ids))
    return user_ids
   
if __name__ == '__main__':
    user_ids = list(demo_df.index)
    gam_df = get_gam_df()
    filt = False
    if filt:
        user_ids = filter_users(user_ids, demo_df=demo_df, gam_df=gam_df)
    else:
        print("No user pre-filtering")
    # features = ["total_hold", "weekly_hold", "weekly_activity", 
    #             "daily_rolling_hold", "total_fixed_live_ratio"]
    #features = SUMMARY_NAMES + WEEKLY_NAMES[0]
    features = ALL_NAMES
    for months in [6]:
        print(f"Constructing model with {months} months of information")
        print(f"Features being used: {features}")
        X, y = featurize(user_ids, gam_df, features=features, month_window=months)
        X_train, X_test, y_train, y_test, user_train, user_test = train_test_split(X, y, user_ids)
        regressor = train_random_forest(X_train, y_train, do_grid=True)
        predict_and_store(regressor, user_test, X_test, y_test, store_name="validation")