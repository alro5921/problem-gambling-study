import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams
import pipeline
from plot_helper import (save_image, plot_ts, add_intervention, add_inter_rg,
                        highlight_weekend_periodicity)
from sklearn.metrics import roc_curve
import imageio

ALL_PRODS = list(range(1,30))
DEFAULT_CUTOFFS = ['2008-02-01', '2008-04-15', '2008-08-01',
             '2008-11-01', '2009-02-05', '2009-05-15'] 

demo_df = pipeline.demo_pipeline() # Global vars weee
gam_df = pipeline.gambling_pipeline()
rg_info = pipeline.rg_pipeline()

def background_plot(ax, user_id):
    '''Plots the introductory "Wow people lose a lot on this" graph'''
    ts = pipeline.accum_by_date(gam_df, user_id, ALL_PRODS)
    ts['cumul_hold'] = ts['hold'].cumsum()
    ax.set_title(f'Cumulative Loss for User #{user_id}')
    ax.set_xlabel("Date", fontsize=16)
    ax.set_ylabel("Loss (Euros)", fontsize=16)
    ax.tick_params(axis="both", labelsize=14)
    ax.set_xlim(left=np.datetime64("2006-01-01"))
    add_inter_rg(ax, rg_info, user_id)
    plot_ts(ax, ts, plt_column='cumul_hold')
    ax.legend()
    save_image(f"background_plot")

def quick_activity_plot(ax, user_id):
    ts = pipeline.accum_by_date(gam_df, user_id, ALL_PRODS)
    plot_ts(ax, ts, plt_column='weighted_bets')
    ax.set_title(f'Weighted Number of Bets for #{user_id}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Weighted #Bets Placed")

def infer_reopen_plot(ax, user_id, show_infer=False):
    '''Plots an example of a Reopen ticket, and how it could be inferred if possible'''
    ts = pipeline.accum_by_date(gam_df, user_id, ALL_PRODS, demographic_df=demo_df)
    plot_ts(ax, ts, plt_column='weighted_bets')
    inter_args = {'linestyle' : "--", 'label' : f'Recorded Intervention', 
                'color' : 'black', 'lw' : 2, 'alpha' : .6}
    add_inter_rg(ax, rg_info, user_id, line_args = inter_args)
    ax.set_title(f'Weighted Number of Bets for #{user_id}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Weighted #Bets Placed")
    ax.set_xlim(left=np.datetime64("2008-04-01"), right=np.datetime64("2009-09-01"))
    if show_infer:
        line_args = {'linestyle' : "--", 'color' : 'green',
                    'label' : "Inferred Intervention", 'lw' : 2}
        add_intervention(ax, date = pd.to_datetime('2008-09-06'), line_args=line_args)
    ax.legend()
    save_image(f'RG_reopen{show_infer}')

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
    actual, prediction = df['Actual'], df['Prediction']
    fpr, tpr, thresholds = roc_curve(actual, prediction)
    x = np.linspace(0, 1, 100)
    ax.plot(fpr, tpr, color='firebrick', label="Random Forest ROC")
    ax.plot(x, x, linestyle='--', color ='black')
    ax.set_xlabel('False Positive Rate (FPR)', fontsize=16)
    ax.set_ylabel('True Positive Rate (TPR)', fontsize=16)
    ax.tick_params(axis="both", labelsize=14)
    ax.set_title('ROC Curve for Random Forest Model')
    ax.legend()
    save_image("roc_curve")

def make_frame(ax, ts, cutoff):
    '''Plots one frame of the framing gif'''
    ts.loc[ts['weighted_bets'] > 10,'weighted_bets'] = 10
    ts_args = {'linewidth' : .7, 'alpha' : .3, 'color': "blue"}
    plot_ts(ax, ts, plt_column='weighted_bets', line_args=ts_args)
    
    rg_date = pd.to_datetime('2009-04-28')
    inter_params = {'linestyle' : "--", 'label' : "RG Event", 'color' : 'black', 'lw' : 2}
    add_intervention(ax, date=rg_date, line_args = inter_params)
    ax.set_title(f'Frame with Cutoff Date {cutoff}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Weighted #Bets Placed")
    ax.set_xlim(left=np.datetime64("2007-01-01"), right=np.datetime64("2010-01-01"))
    
    look_color = 'green' if rg_date > cutoff and rg_date < cutoff + + np.timedelta64(360, 'D') else 'red'
    min_date = max(np.datetime64('2007-01-01'), cutoff - np.timedelta64(540, 'D'))
    ax.fill_between([min_date,cutoff], [12,12], color='gray', alpha=.6)
    max_date = min(np.datetime64('2010-03-01'), cutoff + np.timedelta64(360, 'D'))
    ax.fill_between([cutoff, max_date], [12,12], color=look_color, alpha=.6)
    ax.legend()

def display_frame_shifts(debug=False, cutoffs=DEFAULT_CUTOFFS, user_id=4523711):
    '''Makes the demonstration gif of the frame shifting'''
    cutoffs = [np.datetime64(date) for date in cutoffs]
    images = []
    for cutoff in cutoffs:
        fig, ax = plt.subplots(1, figsize = (10,5))
        ts = pipeline.accum_by_date(gam_df, user_id, ALL_PRODS)['2006-11-01':'2010-03-01']
        make_frame(ax, ts, cutoff)
        if debug:
            plt.show()
        else:
            save_image(f"frame_gif/frame{cutoff}")
            images.append(imageio.imread(f"images/frame_gif/frame{cutoff}.png"))
    if not debug:
        imageio.mimsave('images/frame_show.gif', images, duration=1.5)

if __name__ == '__main__':
    background = False
    if background:
        user_id = 2062223
        fig, ax = plt.subplots(figsize=(10,6))
        background_plot(ax, user_id)
        plt.show()

    reopen_show = False
    if reopen_show:
        user_id = 6237129
        fig, ax = plt.subplots(figsize=(8,5))
        infer_reopen_plot(ax, user_id, show_infer = True)
        plt.show()

    show_weekend = False
    if show_weekend:
        user_id = 1137771
        fig, ax = plt.subplots(figsize=(10,6))
        show_weekend_periodicity(ax, user_id)
        plt.show()

    make_roc = True
    if make_roc:
        path = 'data/model_results/validation_prediction_results2020-08-27 17:44:18.327415.csv'
        fig, ax = plt.subplots(figsize=(9,5))
        show_roc_curve(ax, path)
        plt.show()

    show_frames = True
    if show_frames:
        display_frame_shifts()