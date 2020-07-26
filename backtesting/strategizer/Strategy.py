from operator import itemgetter
import DataFetcher 


class Strategy:
    def __init__(
            self, 
            name,
            check_entry_criteria, 
            check_exit_criteria, 
            stop_loss_rate,
            reward_goal_rate,
            asset_symbol,
            allocation_rate
        ):
        self.name = name
        self.check_entry_criteria = check_entry_criteria
        self.check_exit_criteria =  check_exit_criteria
        self.stop_loss_rate = stop_loss_rate
        self.reward_goal_rate = reward_goal_rate
        self.asset_symbol = asset_symbol
        self.allocation_rate = allocation_rate
        
        self.position_id = None
        self.has_entered_position = False
        self.position_enter_price = None
        self.position_order_size = None
        self.position_exit_price = None
        self.stop_loss = None
        self.reward_goal = None
        
    
    def ingest_data(self, portfolio, time_series, is_final_time_series):
        time_series = time_series.iloc[::-1]
        
        if not self.has_entered_position:
            should_enter_response = self.check_entry_criteria(time_series)
            should_enter, enter_price, enter_type = itemgetter(
                "should_enter", 
                "enter_price", 
                "enter_type"
            )(should_enter_response)
            if should_enter:
                self.has_entered_position = True
                self.position_enter_price = enter_price
                self.stop_loss = enter_price - (self.stop_loss_rate * enter_price)
                self.reward_goal = enter_price + (self.reward_goal_rate * enter_price)
                self.position_order_size = (portfolio.available_capital * self.allocation_rate) / enter_price
                self.position_id = portfolio.enter_position(
                    self.asset_symbol, 
                    enter_price, 
                    self.position_order_size, 
                    enter_type
                )
                return
        
        if self.has_entered_position and not bool(self.position_exit_price):
            should_exit_response = self.check_exit_criteria(
                time_series, 
                self.stop_loss, 
                self.reward_goal,
                is_final_time_series
            )
            should_exit, exit_price, exit_type = itemgetter(
                "should_exit", 
                "exit_price", 
                "exit_type"
            )(should_exit_response)
            
            if should_exit:
                self.position_exit_price = exit_price
                portfolio.exit_position(self.position_id, self.position_exit_price)
                return