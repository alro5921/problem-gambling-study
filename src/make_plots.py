import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams
import pipeline
from plot_helper import (save_image, plot_ts, add_intervention, add_inter_rg,
                        highlight_weekend_periodicity)
from sklearn.metrics import roc_curve

demo_df = pipeline.demo_pipeline()
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

def infer_reopen_plot(ax, user_id):
    all_prods = list(range(1,30))
    ts = pipeline.accum_by_date(gam_df, user_id, all_prods, demographic_df = demo_df)
    plot_ts(ax, ts, plt_column = 'weighted_bets', rg_info = rg_info)
    ax.set_title(f'Weighted Number of Bets for #{user_id}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Weighted Bets")
    line_args = {'linestyle' : "--", 'color' : 'green',
                'label' : "Inferred Intervention", 'alpha' : .5}
    add_intervention(ax, date = pd.to_datetime('2008-09-06'), line_args = line_args)
    add_inter_rg(ax, rg_info, user_id)
    ax.legend()
    save_image("RG_reopen")

def show_weekend_periodicity(ax, user_id):
    prods = [1,2]
    ts = pipeline.accum_by_date(gam_df, user_id, prods, demographic_df = demo_df)['2005-08-01':'2005-10-01']
    plot_ts(ax, ts, plt_column = 'weighted_bets', rg_info = rg_info)
    ax.set_title(f'Weighted Number of Bets for #{user_id}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Weighted Bets")
    highlight_weekend_periodicity(ax, ts)
    save_image("weekend_period")

def show_roc_curve(ax, results_path):
    df = pd.read_csv(results_path)
    actual, prediction = df['Actual'], df['Prediction']
    fpr, tpr, thresholds = roc_curve(actual, prediction)
    x = np.linspace(0, 1, 100)
    ax.plot(fpr, tpr, color='firebrick')
    ax.plot(x, x, linestyle='--', color ='black', label='Random Guess')
    ax.set_xlabel('False Positive Rate (FPR)', fontsize = 16)
    ax.set_ylabel('True Positive Rate (TPR)', fontsize = 16)
    ax.set_title('ROC Curve for Random Forest Model')
    ax.legend()
    save_image("roc_curve")

if __name__ == '__main__':
    reopen_show = False
    if reopen_show:
        user_id = 6237129
        fig, ax = plt.subplots(figsize=(20,12))
        infer_reopen_plot(ax, user_id)
        plt.show()
    show_weekend = False
    if show_weekend:
        user_id = 1137771
        fig, ax = plt.subplots(figsize=(20,12))
        show_weekend_periodicity(ax, user_id)
        plt.show()
    make_roc = True
    if make_roc:
        path = 'data/model_results/validation_prediction_results.csv'
        fig, ax = plt.subplots(figsize=(10,6))
        show_roc_curve(ax, path)
        plt.show()