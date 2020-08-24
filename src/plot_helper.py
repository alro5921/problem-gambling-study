import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams
import pipeline
#from constants import TEAM_CODES

rcParams.update({'figure.autolayout': True})
plt.style.use('ggplot')

def save_image(name, folder_path = 'images'):
    file_path = folder_path + f'/{name}.png'
    plt.savefig(file_path)

def plot_ts(ax, ts, plt_column = 'hold_cum', label = None, rg_info = None, user_id = None):
    if not label:
        label = plt_column
    ax.plot(ts[plt_column], label = plt_column)
    #ax.bar(ts.index, ts[plt_column], label = plt_column)

def infer_reopen(ts):
    pass

def add_intervention(ax, date = None, line_args = None):
    if not line_args:
        line_args = {'linestyle' : "--", 'label' : "Intervention", 'color' : 'black'}
    ax.axvline(date,**line_args)

def add_inter_rg(ax, rg_info, user_id, line_args = None):
    if not user_id in rg_info.index:
        return
    first_rg = rg_info.loc[user_id, 'first_date']
    rg_desc = rg_info.loc[user_id, 'ev_desc']
    inter_desc = rg_info.loc[user_id, 'inter_desc']
    if not line_args:
        line_args = {'linestyle' : "--", 'label' : f'RG: {rg_desc}\nInt:{inter_desc}',
                     'color' : 'black'}
    add_intervention(ax, date = first_rg, line_args = line_args)

def highlight_weekend_periodicity(ax, ts):
    weekends = []
    #weekends = [i for i, ind in enumerate(ts.index) if ind.weekday()]
    for i, ind in enumerate(ts.index):
        if ind.weekday() >= 4:
            weekends.append(i)
    #breakpoint()
    for i_day in weekends[:-1]:
        ax.axvspan(ts.index[i_day], ts.index[i_day + 1], facecolor='gray', edgecolor='none', alpha=.3)

if __name__ == '__main__':
    demo_df = pipeline.demo_pipeline()
    gam_df = pipeline.gambling_pipeline()
    rg_info = pipeline.rg_pipeline()
    
