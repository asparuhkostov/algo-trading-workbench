import requests


COMMISION_RATE = 0.0


class Broker:
    def __init__(self, api_key):
        self.api_key = api_key
    
    
    def place_order(self, portfolio, order_price, order_size, order_type):
        # TO-DO: add Alpaca integration
        pass
    