import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pipeline

def plot_ts(ax, ts, user_id, plt_column = 'hold_cum', rg_info = None):
    ax.plot(ts[plt_column], label = plt_column)
    #ts['num_bets'].plot(label = "Cumulative Loss")
    if rg_info and (user_id in rg_info.index):
        first_rg = rg_info.loc[user_id, 'first_date']
        rg_desc = rg_info.loc[user_id, 'ev_desc']
        inter_desc = rg_info.loc[user_id, 'inter_desc']
        print(rg_info.loc[user_id, 'events'])
        ax.axvline(first_rg, linestyle = "--", label = f'RG: {rg_desc}\nInt:{inter_desc}', color = 'black')