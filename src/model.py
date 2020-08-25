import numpy as np
import pandas as pd
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

def train_random_forest(X,y):
    random_forest_grid = {'max_depth': [3, 5, None],
                        'max_features': ['sqrt', 'log2', None],
                        'min_samples_split': [2, 4, 8],
                        'min_samples_leaf': [1, 5, 10, 20],
                        'bootstrap': [True, False],
                        'n_estimators': [100, 200],
                        'random_state': [1]}
    rf_gridsearch = RandomizedSearchCV(RandomForestClassifier(),
                                random_forest_grid,
                                n_iter = 20,
                                n_jobs=-1,
                                verbose=True,
                                scoring='f1')
    rf_gridsearch.fit(X_train, y_train)
    print("Random Forest best parameters:", rf_gridsearch.best_params_)
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

    demo_cut = demo_df['registration_date'] < '2007-01-01'
    n_app_mask = rg_df['event_type_first'] != 2
    non_appeals = rg_df[n_app_mask]
    z = non_appeals.join(demo_df, 'user_id')
    z = z[z['registration_date'] < '2007-01-01']
    no_rg_ids = list(demo_cut[demo_df['rg'] == 0].index)
    user_ids = list(z.index) + no_rg_ids
    print(len(user_ids))
    X, y = featurize(user_ids)
    X_train, X_test, y_train, y_test = train_test_split(X,y)
    regressor = train_random_forest(X_train, y_train)
    y_pred = regressor.predict_proba(X_test)[:,1] >= .5
    scores(y_test,y_pred)