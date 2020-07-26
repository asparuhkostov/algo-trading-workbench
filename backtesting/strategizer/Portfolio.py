import math
import uuid
import datetime


COMMISION_RATE = 0.0


class Portfolio:    
    def __init__(self, available_capital, minimal_acceptable_return, annual_returns):
        self.positions = []
        self.start_capital_amount = available_capital
        self.available_capital = available_capital
        self.minimal_acceptable_return = minimal_acceptable_return
        self.annual_returns = annual_returns
        self.strategies = []
        self.equity_per_day = []
    
    
    def get_positions(self):
        # TO-DO: add SQLite database instead of keeping positions in-memory
        return self.positions
    
    
    def add_strategy(self, strategy):
        self.strategies.append(strategy)
    
    
    def feed_time_series(self, strategy_name, time_series, is_final_time_series):
        for s in self.strategies:
            if s.name == strategy_name:
                s.ingest_data(self, time_series, is_final_time_series)


    def close_period(self, period_return):
        self.annual_returns.append(period_return)
    
    
    def register_equity_for_day(self, index, equity):
        self.equity_per_day.append({"date": index, "equity": equity})

    
    def enter_position(self, symbol, order_price, order_size, order_type = "buy"):
        order_cost = order_size * order_price
        commision = order_cost * COMMISION_RATE
        total_order_cost = order_cost + commision
        
        if self.available_capital >= total_order_cost:
            # TO-DO: add actual call to broker for orders placing
            new_position = {
                "id": uuid.uuid4(),
                "symbol": symbol,
                "order_type": order_type,
                "order_size": order_size,
                "order_price": order_price,
                "entry": datetime.datetime.now(),
                "exit": None
            }
            self.positions.append(new_position)
            # TO-DO: adjust for slippage
            # TO-DO: add functionality for shorting
            self.available_capital -= total_order_cost
            return new_position["id"]
    
    
    def exit_position(self, position_id, exit_price):
        for index, position in enumerate(self.positions):
            if position.get("id", None) == position_id:
                # TO-DO: add actual call to broker for position closing
                position["exit"] = datetime.datetime.now()
                self.available_capital += exit_price * position["order_size"]
                return