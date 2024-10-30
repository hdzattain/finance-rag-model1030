import backtrader as bt

class MovingAverageStrategy(bt.Strategy):
    def __init__(self):
        self.sma1 = bt.ind.SMA(period=10)
        self.sma2 = bt.ind.SMA(period=20)

    def next(self):
        if self.sma1 > self.sma2:
            self.buy()
        elif self.sma1 < self.sma2:
            self.sell()

def run_backtest():
    cerebro = bt.Cerebro()
    data = bt.feeds.YahooFinanceCSVData(dataname="data/AAPL.csv")
    cerebro.adddata(data)
    cerebro.addstrategy(MovingAverageStrategy)
    cerebro.run()
    cerebro.plot()

run_backtest()