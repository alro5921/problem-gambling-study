'''Functions that construct features from a frame,
to be used in featurizing'''

'''Summary Features'''
def total_hold(frame):
    return frame['hold'].sum()

def max_hold(frame):
    return frame['hold'].max()

def total_activity(frame):
    return frame['weighted_bets'].sum()

def max_diff(frame):
    '''The max difference of hold between two (non-zero) days,
    trying to capture loss chasing'''
    non_zero = frame[frame.hold > 0]
    hold_diff = non_zero['hold'].diff().dropna()
    if len(hold_diff) == 0:
        return 0
    return hold_diff.max()

def total_fixed_live_ratio(frame):
    fixed_hold, live_action_hold = frame['hold_1'].sum(), frame['hold_2'].sum()
    if fixed_hold == 0:
        return 10
    return min(live_action_hold/fixed_hold, 10)

def total_nonzero_hold_std(frame):
    ''' Gambling behavior is relatively sparse,
    seems more useful to look at variance in 
    the bets thesmelves.'''
    frame_nonzero = frame[frame['hold'] > 0]
    if len(frame_nonzero) == 0:
        return 0
    stdev = frame_nonzero['hold'].std()
    if not isinstance(stdev, float):
        breakpoint()
    return max(10000, frame_nonzero['hold'].std())

'''Features on a daily granularity'''
def daily_hold(frame):
    return frame['hold'].values

def daily_rolling_hold(frame):
    return frame['hold'].rolling(5).sum()[4:].values

'''Features on a weekly granularity'''
def agg(frame, d):
    resamp = frame.resample(f'{d}D').sum()
    return resamp

def to_weekly(frame):
    return agg(frame, 7)

def weekly_max(frame):
    weekly_max = frame.resample(f'7D').max()
    return weekly_max['hold'].values

def weekly_hold(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['hold'].values

def weekly_activity(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['weighted_bets'].values

def weekly_rolling_hold(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['hold'].rolling(5).sum()[4:].values

def weekly_rolling_activity(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['weighted_bets'].rolling(5).sum()[4:].values

def weekly_fixed_live_ratio(frame):
    weekly_sum = to_weekly(frame)
    return weekly_sum['num_bets_2']/(1+weekly_sum['num_bets_1'])

SUMMARY_FEATURES = [total_hold, max_hold, max_diff, total_activity, total_fixed_live_ratio, total_nonzero_hold_std]
#total_fixed_live_ratio, total_nonzero_hold_std were busts
SUMMARY_NAMES = [feat.__name__ for feat in SUMMARY_FEATURES]

DAILY_FEATURES = [daily_hold, daily_rolling_hold]
DAILY_NAMES = [feat.__name__ for feat in DAILY_FEATURES]

WEEKLY_FEATURES = [weekly_hold, weekly_activity, weekly_max, weekly_rolling_hold, weekly_rolling_activity, weekly_fixed_live_ratio]
WEEKLY_NAMES = [feat.__name__ for feat in WEEKLY_FEATURES]

ALL_FEATURES = SUMMARY_FEATURES + DAILY_FEATURES + WEEKLY_FEATURES
ALL_NAMES = [feat.__name__ for feat in ALL_FEATURES]

if __name__ == '__main__':
    print("Testing if all the features work (or at least compile)")