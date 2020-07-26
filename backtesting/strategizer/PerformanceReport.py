import math
import pandas as pd


class PerformanceReport:
    def __init__(self):
        pass
    
    
    def calculate_maximum_drawdown(self, portfolio):
        portfolio_equity_values = []
        
        for e in portfolio.equity_per_day:
            portfolio_equity_values.append(e["equity"])
        
        portfolio_equity_values = pd.Series(portfolio_equity_values)
        window = len(portfolio.equity_per_day)
        
        rolling_max = portfolio_equity_values.cummax()
        daily_drawdown = portfolio_equity_values / rolling_max - 1.0
        max_daily_drawdown = daily_drawdown.cummin()
        
        mdd = 0
        for m in max_daily_drawdown.values:
            if m < mdd:
                mdd = m
        
        return str(round(mdd, 3) * 100) + "%"
    
    
    def calculate_downside_deviation(self, annual_returns, minimal_acceptable_return):
        squared_negative_annual_returns = []
        downside_deviation = 0
        
        for ar in annual_returns:
            ar -= minimal_acceptable_return
            if ar < 0:
                squared_negative_annual_returns.append(pow(ar, 2))
        
        if len(squared_negative_annual_returns) > 0:       
            downside_deviation = math.sqrt(
                sum(squared_negative_annual_returns) / 
                len(squared_negative_annual_returns)
            )
        
        return downside_deviation
    
    
    def calculate_annual_return_rate(self, portfolio):
        annual_return = portfolio.available_capital - portfolio.start_capital_amount
        annual_return_rate = annual_return / portfolio.start_capital_amount
        return annual_return_rate
    
    
    def calculate_omega_ratio(self, portfolio):
        omega_ratio = None
        annual_returns = portfolio.annual_returns
        n = len(annual_returns)
        threshold = portfolio.minimal_acceptable_return
        upside = 0
        downside = 0
        
        for i in range(n-1):
            n_return = annual_returns[i]
            if n_return < threshold:
                downside += threshold - n_return
            if n_return > threshold:
                upside += n_return - threshold
        
        if downside > 0:
            omega_ratio = round(upside / downside, 2)
        else:
            omega_ratio = "-"
        
        return omega_ratio
    
    
    def generate_report(self, portfolio):
        # TO-DO - actually annualize the return rates here
        # TO-DO - decide how to deal with the dummy annual returns
        # TO-DO - decide on source for risk free rate
        risk_free_rate = 0.025
        sortino_ratio = "-"
        
        
        minimal_acceptable_return = portfolio.minimal_acceptable_return
        annual_return_rate = self.calculate_annual_return_rate(portfolio)
        portfolio.close_period(annual_return_rate)
        
        downside_deviation = self.calculate_downside_deviation(
            portfolio.annual_returns, 
            portfolio.minimal_acceptable_return
        )
        
        if downside_deviation != 0:
            sortino_ratio = round((annual_return_rate - risk_free_rate) / downside_deviation, 2)
        
        omega_ratio = self.calculate_omega_ratio(portfolio)
        
        return {
            "annual_return_rate": str(round(annual_return_rate * 100, 2)) + '%',
            "maximum_drawdown": self.calculate_maximum_drawdown(portfolio),
            "omega_ratio": omega_ratio,
            "sortino_ratio": sortino_ratio
        }
    
    
    def get_portfolio_equity_curve(self, portfolio):
        x_axis_data = []
        y_axis_data = []
        
        for d in portfolio.equity_per_day:
            x_axis_data.append(d["date"])
            y_axis_data.append(d["equity"])
        
        return {"x": x_axis_data, "y": y_axis_data}