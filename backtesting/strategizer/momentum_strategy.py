import ta as ta


'''
for this simple strategy the rules are:
    1. RSI > 60 for 3 days in a row
    2. OBV is higher for 3 days in a row
    3. MACD of last 50 is higher than 200 days average 
''' 
def check_entry_criteria(time_series):
    is_overbought = True
    is_obv_positive = True
    is_macd200_higher = True
    enter_price = None
    
    rsi_instance = ta.momentum.RSIIndicator(
        close = time_series["adjusted_close"], 
        n = 50, 
        fillna = True
    )
    rsi_data = rsi_instance.rsi()
    rsi_last_3_days = rsi_data.head(3)
    for d in rsi_last_3_days:
        if d < 60:
            is_overbought = False
            break
    
    obv_instance = ta.volume.OnBalanceVolumeIndicator(
        close = time_series["adjusted_close"],
        volume = time_series["volume"],
        fillna = True
    )
    obv_data = obv_instance.on_balance_volume()
    obv_data_last_3_days = obv_data.head(3)
    for d in obv_data_last_3_days:
        if d < 0:
            is_obv_positive = False
            break
    
    macd_instance = ta.trend.MACD(
        close = time_series["adjusted_close"],
        n_fast = 50,
        n_slow = 200,
        fillna = True
    )
    macd_data = macd_instance.macd_diff()
    macd_data_in_last_3_days = macd_data.head(3)
    for d in macd_data_in_last_3_days:
        if d < 0:
            is_macd200_higher = False
            break
            
    enter_price = time_series.head(1)["adjusted_close"].values[0]
    
    return {
        "should_enter": is_overbought and is_obv_positive and is_macd200_higher,
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