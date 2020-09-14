import numpy as np
import pandas as pd
from datetime import datetime
from featurizing import featurize_backward, featurize_forward
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import pipeline 
import random
import time
from data_cleaning import create_gam_df, sparse_to_ts

demo_df = pipeline.demo_pipeline()
#gam_df = pipeline.gambling_pipeline()
rg_df = pipeline.rg_pipeline()

def train_grad_boost(X_train, y_train, do_grid=False):
    grad_boost_grid = {'learning_rate': [0.05, 0.02, 0.01, 0.005],
                                'max_depth': [3, 5],
                                'min_samples_leaf': [5, 10, 50, 100, 200],
                                'max_features': [2, 3, 5, 10],
                                'n_estimators': [150, 300, 500, 1000],
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
    '''A logistic model just on the total amount o; using this as a baseline'''
    log_model = LogisticRegression(max_iter=500)
    log_model.fit(X_train, y_train)
    return log_model

GRID_SEARCH_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 2,
                     'min_samples_leaf': 5, 'max_features': None, 'max_depth': None, 'bootstrap': True}

LOOKFORWARD_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 4, 
                    'min_samples_leaf': 1, 'max_features': 'sqrt', 'max_depth': None, 'bootstrap': False}


def train_random_forest(X_train, y_train, do_grid=False):
    '''Trains a random forest model on the training frames, doing grid_search if needed'''
    if not do_grid:
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
                                n_iter = 100,
                                n_jobs=-1,
                                verbose=True,
                                scoring='f1')
    rf_gridsearch.fit(X_train, y_train)
    print("Random Forest RGS parameters:", rf_gridsearch.best_params_)
    regressor = rf_gridsearch.best_estimator_
    return regressor

def scores(y_test,y_pred):
    confus = confusion_matrix(y_test,y_pred)
    tn, fp, fn, tp = confus.ravel()
    print(f'True Neg {tn}, False Pos {fp}, False Neg {fn}, True Positive {tp}')
    print(f'Accuracy: {accuracy_score(y_test,y_pred)}')
    print(f'Recall: {recall_score(y_test, y_pred)}')
    print(f'Precision: {precision_score(y_test,y_pred)}')
    print(f'F1: {f1_score(y_test,y_pred)}')

def predict_and_store(model, user_ids, X_test, y_test, store_name="", verbose=True, thres=.5):
    y_prob = model.predict_proba(X_test)[:,1]
    val_store = pd.DataFrame({"id": user_ids, "actual" : y_test, "prediction" : y_prob})
    now = datetime.now()
    val_store.to_csv(f'data/model_results/{store_name}_prediction_results{now}.csv')

    y_pred = (y_prob >= thres).astype(int)
    if(verbose):
        scores(y_test,y_pred)
    return y_prob

def create_user_set(user_dict, demo_df, gam_df):
    print("Entering set creation")
    ids = pipeline.filter_low_activity(user_dict, gam_df=gam_df)
    demo_filt = demo_df[demo_df.index.isin(ids)]
    rg_ids = list(demo_filt[demo_filt['rg'] == 1].index)
    no_rg_ids = list(demo_filt[demo_filt['rg'] == 0].index)
    return rg_ids, no_rg_ids

import time
# your code here    
if __name__ == '__main__':
    user_ids = list(demo_df.index)
    print("Using new stuff")
    start = time.process_time()
    gam_df = create_gam_df()
    #rg_ids, no_rg_ids = create_user_set(user_dict, demo_df=demo_df, gam_df=gam_df)
    #user_ids = rg_ids + random.choices(no_rg_ids, k=2000)
    #print(len(rg_ids))
    #print(len(no_rg_ids))
    #print(len(user_ids))
    # Random state to preserve same holdout (ideally I'd make MUCH more sure than this)
    train_ids, holdout_ids = train_test_split(user_ids, random_state=104, shuffle=True)
    #features = ["total_hold"]
    features = ["total_hold", "weekly_hold", "weekly_activity", "total_fixed_live_ratio"]
    for look_forward in [1,3,6,9,12,24]:
        print(f"Beginning model with {look_forward} month look forward")
        start = time.process_time()
        X, y = featurize_forward(train_ids, gam_df, features=features, look_forward=look_forward)
        print(time.process_time() - start)
        X_train, X_test, y_train, y_test, user_train, user_test = train_test_split(X, y, train_ids)
        regressor = train_random_forest(X_train, y_train, do_grid=False)
        predict_and_store(regressor, user_test, X_test, y_test, store_name="validation")
    ##
    run_hold = False
    if run_hold:
        print("=========")
        X_hold, y_hold = featurize(holdout_ids)
        predict_and_store(regressor, X_hold, y_hold, store_name="holdout")
