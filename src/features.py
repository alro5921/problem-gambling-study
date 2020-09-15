'''Constructing features from a frame'''

def total_hold(frame):
    return frame['hold'].sum()

def max_hold(frame):
    return frame['hold'].max()

def total_activity(frame):
    return frame['weighted_bets'].sum()

import math

def to_weekly(frame):
        # Can have a week "chopped off" or not depending on the exact start date
        # Just imput with the last value if so
    weekly_sum = frame.resample('7D').sum()
    return weekly_sum

def weekly_hold(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['hold'].values

def weekly_activity(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['weighted_bets'].values

def weekly_rolling_hold(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['weighted_bets'].rolling(5).sum()[4:].values

def daily_rolling_hold(frame):
    #frame = pad_lookback(frame, lookback)
    return frame['hold'].rolling(5).sum()[4:].values

def total_fixed_live_ratio(frame):
    fixed_hold, live_action_hold = frame['hold_1'].sum(), frame['hold_2'].sum()
    if fixed_hold == 0:
        return 10
    return min(live_action_hold/fixed_hold, 10)

# def weekly_fixed_live_ratio(frame, lookback):
#     weekly_sum = frame.resample('M').sum()
#     weekly_sum = pad_lookback(weekly_sum, lookback)
#     return weekly_sum['turnover_2']/(1+weekly_sum['turnover'])

def pad_lookback(aggregate, lookback):
    pad = lookback - len(aggregate)
    if pad > 0:
        aggregate.append(aggregate.iloc[[-1]*pad])
    return aggregate