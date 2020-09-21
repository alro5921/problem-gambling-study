import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import random

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (confusion_matrix, accuracy_score, 
                            precision_score, recall_score, f1_score)

from processing.features import SUMMARY_NAMES, DAILY_NAMES, WEEKLY_NAMES
from processing.preprocessing import preprocessing

from pipeline import get_demo_df, get_gam_df, get_rg_df
from model_constants import *

def train(X, y, base_model, do_grid=True, grid=None, grid_params=None, save=False):
    ''' 
    Performs a cross validated gridsearch on a base model, and returns the best model+gridsearch information.

    Args:
        X: ndarray of all features
        y: ndarray of targets
        base_model: sklearn classifier object to grid search on
        do_grid: default True, if False will just use a guess from previous iterations
        grid: The dictionary grid to run 
        grid_params: Custom parameters to the grid (if needed)
        save: Boolean of whether to save the model and gridsearch outputs in model
    Returns:
        model: The best fit model
        gs_results: Information associated with the gridsearch
    '''
    if not search_params:
        grid_params = DEFAULT_GRID_PARAMS
    gridsearch = RandomizedSearchCV(base_model, grid, scoring='f1', verbose=verbose, **search_params)
    gridsearch.fit(X, y)
    regressor = gridsearch.best_estimator_
    if save:
        save_model(regressor, gridsearch)
    print(f'Model Avg F1 Score: {gridsearch.best_score_:.3f}')
    return regressor, gridsearch
    
def save_model(regressor, gridsearch):
    '''Saves the trained model and gridsearch'''
    now = datetime.now().strftime("%m-%d-%H-%M")
        gs_path = f'model/grid_results_{now}.pkl'
        with open(gs_path, 'wb') as f:
            pickle.dump(gridsearch, f)
        model_path = f'model/model_{now}.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(regressor, f)


def predict(model, X, y=None, user_ids=None, store=True, store_name="", thres=.5, verbose=True):
    ''' Predicts on an existing model, given a featurized X array
    
    Args:
        model: A trained sklearn classifier
        X: Featurized narray of the data to predict
        y: 1D Labels for scoring, if available or needed
        user_ids: 1D User_ids associated with each X, if available or needed
        store: Boolean of whether to store the predicted results
        store_name: Name of the file to store results in 
        threshold: Threshold of y_proba to classify positive, default .5
        verbose: Boolean of whether to print more detailed scoring results
    Returns:
        y_proba: the y_proba array from the classifier
    '''
    y_prob = model.predict_proba(X)[:,1]
    if store:
        store_predictions(y_prob, y, user_ids)
    if verbose and y:
        y_pred = (y_prob >= thres).astype(int)
        scores(y,y_pred)
    return y_prob

def store_predictions(y_prob, y=None, user_ids=None):
    '''Helper for predict, stores the predictions and possible associated labels+user_ids'''
    val_store = pd.DataFrame({"prediction" : y_prob})
    if y:
        val_store["actual"] = y
    if user_ids:
        val_store["id"] = user_ids
    now = datetime.now()
    val_store.to_csv(f'data/model_results/{store_name}_prediction_results{now}.csv')

def scores(y_test,y_pred):
    '''Helper for predict, shows the prediction scores'''
    confus = confusion_matrix(y_test,y_pred)
    tn, fp, fn, tp = confus.ravel()
    print(f'True Neg {tn}, False Pos {fp}, False Neg {fn}, True Positive {tp}')
    print(f'Accuracy: {accuracy_score(y_test,y_pred):.3f}')
    print(f'Recall: {recall_score(y_test, y_pred):.3f}')
    print(f'Precision: {precision_score(y_test,y_pred):.3f}')
    print(f'F1: {f1_score(y_test,y_pred):.3f}')

if __name__ == '__main__':
    months = 6
    feature_sets = [SUMMARY_NAMES, SUMMARY_NAMES[:4] + ['weekly_hold', 'weekly_activity']]
    for features in feature_sets:
        X, y, user_ids = preprocessing(months, features=features)
        X_train, X_test, y_train, y_test, user_train, user_test = train_test_split(X, y, user_ids)
        model, gs = train(X_train, y_train, RandomForestClassifier(), do_grid=True, grid=RF_GRID, save=True)
        predict(model, X_test, y_test, user_test, store_name="ROC")
