import ta as ta
import numpy as np


'''
for this simple strategy the rules are:
    1. z-score should be less than 1, meaning the price is below its mean
''' 
def check_entry_criteria(time_series):
    is_below_mean_value = False
    is_oversold = False
    is_positive_trend = False

    raw_score = time_series["adjusted_close"].head(1).values[0]
    mean = time_series["adjusted_close"].mean()
    z_score = (raw_score - mean) / np.std(time_series["adjusted_close"]) 
    
    if z_score < 0:
        is_below_mean_value = True
        
    rsi_instance = ta.momentum.RSIIndicator(
        close = time_series["adjusted_close"], 
        n = 5, 
        fillna = True
    )
    rsi_data = rsi_instance.rsi()
    rsi_last_2_days = rsi_data.head(2)
    for d in rsi_last_2_days:
        if d < 5:
            is_oversold = True
            break
    
    ma_200 = time_series["adjusted_close"].rolling(window=200, min_periods=1).mean()
    ma_50 = time_series["adjusted_close"].rolling(window=50, min_periods=1).mean()
    if ma_50.head(1).values[0] > ma_200.head(1).values[0]:
        is_positive_trend = True
    
    enter_price = time_series.head(1)["adjusted_close"].values[0]
    
    return {
        "should_enter": is_below_mean_value and is_oversold and is_positive_trend,
        "enter_price": enter_price,
        "enter_type": "buy"
    }


'''
for this exit strategy the rules are:
    1. price is past/at stop loss
    2. price is past/at reward goal
'''
def check_exit_criteria(
        time_series, 
        stop_loss, 
        reward_goal, 
        is_at_max_position_duration
):
    is_price_at_stop_loss = False
    is_price_at_reward_goal = False
    
    exit_price = time_series.head(1)["adjusted_close"].values[0]
    
    if exit_price < stop_loss:
        is_price_at_stop_loss = True
    
    if exit_price > reward_goal:
        # TO-DO: implement trailing stop order to allow for locking in profits while maximizing potential returns
        is_price_at_reward_goal = True
    
    return { 
        "should_exit": is_price_at_stop_loss or is_price_at_reward_goal or is_at_max_position_duration,
        "exit_price": exit_price,
        "exit_type": "sell"
    }