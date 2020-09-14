'''Constructing features from a frame'''

def total_hold(frame):
    return frame['hold'].sum()

def max_hold(frame):
    return frame['hold'].max()

def total_activity(frame):
    return frame['weighted_bets'].sum()

def weekly_hold(frame, lookback):
    weekly_sum = frame.resample('W').sum()
    weekly_sum = pad_lookback(weekly_sum, lookback)
    return weekly_sum['hold'].values[-lookback:]

def weekly_activity(frame, lookback):
    weekly_sum = frame.resample('W').sum()
    weekly_sum = pad_lookback(weekly_sum, lookback)
    return weekly_sum['weighted_bets'].values[-lookback:]

# def weekly_rolling_hold(frame, lookback):
#     weekly_sum = frame.resample('W').sum()
#     pad_lookback(weekly_sum, lookback)
#     w_sum = weekly_sum['weighted_bets'].rolling(5).sum()[4:][-lookback:]
#     breakpoint()
#     return w_sum

def daily_rolling_hold(frame, lookback):
    frame = pad_lookback(frame, lookback)
    frame['hold'].rolling(5).sum()[4:][-lookback:]

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