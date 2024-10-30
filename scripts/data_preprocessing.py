import yfinance as yf
import pandas as pd

def download_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data.to_csv(f'data/{ticker}.csv')
    return data

# 示例：下载Apple股票数据
download_stock_data("AAPL", "2021-01-01", "2022-01-01")