import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams
import pipeline

rcParams.update({'figure.autolayout': True})
plt.style.use('ggplot')

def save_image(name, folder_path='images', args={}):
    file_path = folder_path + f'/{name}.png'
    plt.savefig(file_path, **args)

def plot_ts(ax, ts, plt_column='hold_cum', line_args={}):
    ax.plot(ts[plt_column], **line_args)

def add_intervention(ax, date=None, line_args=None):
    if not line_args:
        line_args = {'linestyle' : "--", 'label' : "Intervention", 'color' : 'black'}
    ax.axvline(date, **line_args)

def add_inter_rg(ax, rg_info, user_id, line_args=None):
    if not user_id in rg_info.index:
        return
    first_rg = rg_info.loc[user_id, 'first_date']
    rg_desc = rg_info.loc[user_id, 'ev_desc']
    inter_desc = rg_info.loc[user_id, 'inter_desc']
    if not line_args:
        line_args = {'linestyle' : "--", 'label' : f'RG: {rg_desc}', 'color' : 'black'}
    add_intervention(ax, date = first_rg, line_args = line_args)

def dashed_lines_to_point(ax, x, y, line_args=None):
    if not line_args:
        line_args = {'linestyle' : "--", 'color' : 'black', 'linewidth' : 1}
    ax.axhline(y, **line_args, xmax=x)
    ax.axvline(x, **line_args, ymax=y)

if __name__ == '__main__':
    pass
