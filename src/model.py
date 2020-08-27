import numpy as np
import pandas as pd
from datetime import datetime
from featurizing import featurize
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
#from sklearn.model_selection import RandomizedSearchCV
import pipeline 

demo_df = pipeline.demo_pipeline()
rg_df = pipeline.rg_pipeline()

def train_baseline(X_train,y_train):
    '''A Decision tree on just on the total activity; using this as a baseline'''
    log_model = LogisticRegression()
    log_model.fit(X_train, y_train)
    return log_model

GRID_SEARCH_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 2, 'min_samples_leaf': 10,
                     'max_features': None, 'max_depth': None, 'bootstrap': True}

#{'random_state': 1, 'n_estimators': 200, 'min_samples_split': 8, 'min_samples_leaf': 10, 'max_features': 'sqrt', 'max_depth': None, 'bootstrap': False}



def train_random_forest(X_train,y_train, do_grid = False):
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

if __name__ == '__main__':
    look_back = 12
    look_forward = 6

    #demo_cut = demo_df['registration_date'] < '2007-01-01'
    n_app_mask = rg_df['event_type_first'] != 2
    non_appeals = rg_df[n_app_mask]
    # z = non_appeals.join(demo_df, 'user_id')
    # z = z[z['registration_date'] < '2007-01-01']
    no_rg_ids = list(demo_df[demo_df['rg'] == 0].index)
    user_ids = list(non_appeals.index) + no_rg_ids[:300]
    # Random state to preserve same holdout, ideally I'd put this whole data in an entirely seperate thing
    # TIL you can do this one 1-d arrays too
    train_ids, holdout_ids = train_test_split(user_ids, random_state = 104, shuffle = True)
    print(len(train_ids), len(holdout_ids))
    X, y = featurize(train_ids)
    X_train, X_test, y_train, y_test = train_test_split(X,y)
    #regressor = train_baseline(X_train, y_train)
    regressor = train_random_forest(X_train, y_train, do_grid = True)
    y_prob = regressor.predict_proba(X_test)[:,1]
    thres = .5
    y_pred = (y_prob >= thres).astype(int)
    scores(y_test,y_pred)
    val_store = pd.DataFrame({"Actual" : y_test, "Prediction" : y_prob})
    now = datetime.now()
    val_store.to_csv(f'data/model_results/validation_prediction_results{now}.csv')
    ##
    run_hold = False
    if run_hold:
        print("=========")
        X_hold, y_hold = featurize(holdout_ids)
        y_hold_prob = regressor.predict_proba(X_hold)[:,1]
        thres = .5
        y_hold_pred = (y_hold_prob >= thres).astype(int)
        scores(y_hold,y_hold_pred)
        val_store = pd.DataFrame({"Actual" : y_hold, "Prediction" : y_hold_pred})
        val_store.to_csv(f'data/model_results/holdout_prediction_results{now}.csv')
