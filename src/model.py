import numpy as np
import pandas as pd
from datetime import datetime
from featurizing import featurize
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import pipeline 

demo_df = pipeline.demo_pipeline()
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


def train_baseline(X_train,y_train):
    '''A logistic model just on the total amount o; using this as a baseline'''
    log_model = LogisticRegression(max_iter=500)
    log_model.fit(X_train, y_train)
    return log_model

GRID_SEARCH_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 2,
                     'min_samples_leaf': 5, 'max_features': None, 'max_depth': None, 'bootstrap': True}

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
                        'n_estimators': [100, 200],
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

def predict_and_store(model, X_test, y_test, store_name="", verbose=True, thres=.5):
    y_prob = model.predict_proba(X_test)[:,1]
    val_store = pd.DataFrame({"Actual" : y_test, "Prediction" : y_prob})
    now = datetime.now()
    val_store.to_csv(f'data/model_results/{store_name}_prediction_results{now}.csv')

    y_pred = (y_prob >= thres).astype(int)
    if(verbose):
        scores(y_test,y_pred)
    return y_prob

def filter_appeals(users):
    n_app_mask = rg_df['event_type_first'] != 2
    return rg_df[n_app_mask]

def filter_low_hold(users):
    pass


if __name__ == '__main__':
    n_app_mask = rg_df['event_type_first'] != 2
    non_appeals = rg_df[n_app_mask]
    no_rg_ids = list(demo_df[demo_df['rg'] == 0].index)
    user_ids = list(non_appeals.index) + no_rg_ids[:300]
    # Random state to preserve same holdout (ideally I'd make MUCH more sure than this)
    # TIL you can do this one 1-d arrays too
    train_ids, holdout_ids = train_test_split(user_ids, random_state=104, shuffle=True)
    #features = ["total_hold"]
    features = ["total_hold", "weekly_hold", "rolling_hold", "total_fixed_live_ratio"]
    X, y = featurize(train_ids, features=features)
    #breakpoint()
    X_train, X_test, y_train, y_test = train_test_split(X,y)
    regressor = train_random_forest(X_train, y_train, do_grid=True)
    predict_and_store(regressor, X_test, y_test, store_name="validation")
    ##
    run_hold = False
    if run_hold:
        print("=========")
        X_hold, y_hold = featurize(holdout_ids)
        predict_and_store(model, X_hold, y_hold, store_name="holdout")
