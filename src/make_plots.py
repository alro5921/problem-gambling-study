import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams
from plot_helper import *
from sklearn.metrics import roc_curve
import pipeline
from pipeline_constants import *
import imageio

rcParams.update({'figure.autolayout': True})
plt.style.use('ggplot')

demo_df = pipeline.get_demo_df() # Global vars weee
gam_df = pipeline.get_gam_df()
rg_info = pipeline.get_rg_df()

def background_plot(ax, user_id):
    '''Plots the introductory "Wow people lose a lot on this" graph'''
    mask = (gam_df['user_id'] == user_id)
    user_daily = gam_df[mask]
    first_deposit = demo_df.loc[user_id, 'first_deposit_date']
    user_frame = pipeline.sparse_to_ts(user_daily, date_start=first_deposit, window=30*48)
    ts['cumul_hold'] = ts['hold'].cumsum()
    ax.set_title(f'Cumulative Loss for User #{user_id}')
    ax.set_xlabel("Date", fontsize=16)
    ax.set_ylabel("Loss (Euros)", fontsize=16)
    ax.tick_params(axis="both", labelsize=14)
    # ax.set_xlim(left=np.datetime64("2006-01-01"))
    add_inter_rg(ax, rg_info, user_id)
    plot_ts(ax, ts, plt_column='cumul_hold')
    ax.legend()
    save_image(f"background_plot2")

def quick_activity_plot(ax, user_id):
    ts = pipeline.accum_by_date(gam_df, user_id, ALL_PRODS)
    plot_ts(ax, ts, plt_column='weighted_bets')
    ax.set_title(f'Weighted Number of Bets for #{user_id}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Weighted #Bets Placed")
    ax.set_xlim(left=np.datetime64("2006-01-01"))
    add_inter_rg(ax, rg_info, user_id)
    ax.legend()
    save_image(f"activity_plot")

def show_weekend_periodicity(ax, user_id):
    '''Investigate the weekend periodicity (or lack thereof!)'''
    prods = [1,2]
    ts = pipeline.accum_by_date(gam_df, user_id, prods, demographic_df=demo_df)['2005-08-01':'2005-10-01']
    plot_ts(ax, ts, plt_column = 'weighted_bets', rg_info = rg_info)
    ax.set_title(f'Weighted Number of Bets for #{user_id}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Weighted #Bets Placed")
    highlight_weekend_periodicity(ax, ts)
    save_image("weekend_period")

def show_roc_curve(ax, results_path):
    '''Makes a roc curve from the model proba results'''
    df = pd.read_csv(results_path)
    actual, prediction = df['actual'], df['prediction']
    fpr, tpr, thresholds = roc_curve(actual, prediction)
    x = np.linspace(0, 1, 100)
    ax.plot(fpr, tpr, color='firebrick', label="ROC")
    ax.plot(x, x, linestyle='--', color ='black')
    ax.set_xlabel('False Positive Rate (FPR)', fontsize=16)
    ax.set_ylabel('True Positive Rate (TPR)', fontsize=16)
    ax.tick_params(axis="both", labelsize=14)
    #breakpoint()
    #dashed_lines_to_point(ax, fpr[20], tpr[20])
    #ax.set_title('ROC Curve')
    ax.legend()
    save_image("roc_curve")

def show_feature_importances(importances, labels):
    zipper = list(zip(labels, importances))
    zipper.sort(key = lambda p: p[1], reverse = True)
    labels, importances = [p[0] for p in zipper], [p[1] for p in zipper]
    ax.tick_params(axis='x', rotation=15, labelsize=24)
    ax.tick_params(axis='y', labelsize=20)
    ax.set_ylabel("Feature Importance", size=32)
    color_mask = ['#00BA38' if imports > .1 else '#F8766D' 
                for imports in importances]
    ax.bar(labels, importances, color=color_mask, width=.4)
    save_image("summary_feat")

if __name__ == '__main__':
    background = False
    if background:
        user_id = 2062223
        fig, ax = plt.subplots(figsize=(10,6))
        background_plot(ax, user_id)
        plt.show()

    feat_import = False
    if feat_import:
        fig, ax = plt.subplots(figsize=(20,14))
        importances = [0.2742573, 0.15426226, 0.20150834, 0.28402445, 0.07970281, 0.00624484]
        feat_labels = ['Total Loss', 'Max Loss', 'Max Difference', 
                    'Total Activity', 'Fixed-Live Ratio', 'Loss Variance']
        show_feature_importances(importances, feat_labels)
        plt.show()

    eda_three = True
    if eda_three:
        daily_loss = [19.1, 6.1]
        daily_bets = [5.8, 2.6]
        live_actions = [.36, .22]
        fig, ax = plt.subplots(figsize=(15,15))
        plot_compare_bar(ax, daily_loss, "Daily Loss", "Loss (Euros)")
        plt.show()
        save_image("daily_loss")
        fig, ax = plt.subplots(figsize=(15,15))
        plot_compare_bar(ax, daily_bets, "Daily Bets Placed", "Bets Placed")
        plt.show()
        save_image("daily_bet")
        fig, ax = plt.subplots(figsize=(15,15))
        plot_compare_bar(ax, live_actions, "Live Action Usage", "% Live Action")
        plt.show()
        save_image("live_action")

    activity = False
    if activity:
        user_id = 2062223
        fig, ax = plt.subplots(figsize=(8,5))
        quick_activity_plot(ax, user_id)

    show_weekend = False
    if show_weekend:
        user_id = 1137771
        fig, ax = plt.subplots(figsize=(10,6))
        show_weekend_periodicity(ax, user_id)
        plt.show()

    make_roc = False
    if make_roc:
        path = 'data/model_results/ROC_prediction_results2020-09-18 12:53:32.598897.csv'
        fig, ax = plt.subplots(figsize=(9,5))
        show_roc_curve(ax, path)
        plt.show()