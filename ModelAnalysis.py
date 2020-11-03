import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import math 


class ModelAnalysis():
    def __init__(self,start_date, end_date, stock_name):
        self.start_date = start_date
        self.end_date = end_date
        self.stock_name = stock_name
        self.col_name = None
        self.data = pd.DataFrame()
        self.ticker_list = list()
        self.buy_sell_data = pd.DataFrame()
        
        yf.pdr_override()
        
        
    def get_stock_name(self):
        try:
            self.data = pdr.get_data_yahoo(self.stock_name,start=self.start_date,end=self.end_date)
            
            ###startes
            
            self.data['%change'] = np.nan

            for j in range(1,self.data.shape[0]):
                self.data['%change'][j] = ((self.data['Close'][j] - self.data['Close'][j-1])/self.data['Close'][j]) * 100   
            ###endes
            #self.data = self.data.style.applymap(self.color_negative_red)
            return self.data
        except Exception as e:
            return None
            
    
    def get_plot(self,col_name):
        self.col_name = col_name
        title = self.col_name + " Stocks for " + self.stock_name
        fig = px.line(self.data, x=self.data.index, y=self.col_name, title=title)

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
               ])
            )
        )
        
        return fig
    
    def compare_stocks(self, compare_ticker):
            
        Data = pd.DataFrame()
        no_stock_list = list()
        
        for stock in compare_ticker:
            try:
                df = pdr.get_data_yahoo(stock,start=self.start_date,end=self.end_date)
                df['Ticker'] = stock
                df['%change'] = np.nan
                for j in range(1,df.shape[0]):
                    df['%change'][j] = (
                        (df['Close'][j] - df['Close'][j-1])/df['Close'][j])*100
                
                Data = Data.append(df)
                del df
            except Exception as e:
                no_stock_list.append(stock)
        
        Title = "Compare stocks with " 
        length = 0
        for s in compare_ticker:
            if length == len(compare_ticker) - 1:
                Title += s
            else:
                Title += s + " and "
                length += 1
                    
        
        fig = px.line(Data, x=Data.index, y=self.col_name, color='Ticker',title=Title)
        
        return fig, no_stock_list
    
    def ewa_sma(self):
        EMA = self.data[self.col_name].ewm(span=20, adjust = False).mean()
        SMA = self.data[self.col_name].rolling(window=20).mean()
        self.data['EMA'] = EMA
        self.data['SMA'] = SMA
        #df = self.data[self.data[self.col_name] == self.stock_name]
        #df[df['name'] == 'name']
        
        fig = px.line(self.data, x=self.data.index, y=self.col_name)

        fig.add_scatter(x=self.data.index, y=self.data['EMA'], mode='lines',name='Expotential Weighted Avg')
        
        return fig
    
    def candle_plot(self):
        fig = go.Figure(data=[go.Candlestick(x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'])])
        
        return fig
    
    def color_negative_red(self, val):
        color = 'red' if val < 0 else 'black'
        return 'color: %s' % color
    
    
    def buy_sell(self, ticker_list):
        self.ticker_list = ticker_list
        today = datetime.date.today()
        prev = today - datetime.timedelta(days=4)
        
        for ticker in self.ticker_list:
            try:
                df = pdr.get_data_yahoo(
                    ticker,
                    start=prev,
                    end=dt.datetime.now()).iloc[-1:,:]
                df['Ticker'] = ticker
                self.buy_sell_data = self.buy_sell_data.append(df)
                del df
            except Exception as e:
                pass
            
        self.buy_sell_data['Buy'] = "don't buy"
        self.buy_sell_data['Sell'] = "don't sell"

        for i in range(self.buy_sell_data.shape[0]):
            if np.floor(self.buy_sell_data['Open'][i]) == np.floor(self.buy_sell_data['Low'][i]):
                self.buy_sell_data['Buy'][i] = "Buy"
            elif np.floor(self.buy_sell_data['Open'][i]) == np.floor(self.buy_sell_data['High'][i]):
                self.buy_sell_data['Sell'][i] = "Sell"
            else:
                pass
        
        value_change = []
        data = pd.DataFrame()
        today = datetime.date.today()
        prev = today - datetime.timedelta(days=4)
        #curr = datetime.date.today()
        
        for i in range(len(self.ticker_list)):
            try:
                df = pdr.get_data_yahoo(self.ticker_list[i],start=prev,end=dt.datetime.now())
                df['ticker'] = self.ticker_list[i]
                df['change'] = np.nan

                for j in range(1,df.shape[0]):
                    df['change'][j] = ((df['Close'][j] - df['Close'][j-1])/df['Close'][j]) * 100
                    #print(df['change'][j])
                #value_change.append(df.iloc[-1:,-1:]['change'][0])
                data = data.append(df)
                del df
            except Exception as e:
                print("No data available for {}".format(self.ticker_list[i]))
         
        
                
            
        self.buy_sell_data['change'] = np.nan
        
        #for i in range(2,data.shape[0],3):
        #    value_change.append(data['change'][i])
            
        #self.buy_sell_data['%_change'] = value_change
        
        #self.buy_sell_data.style.applymap(self.color_negative_red)
        
        data['count'] = np.nan

        for i in range(data.shape[0]):
            data['count'][i] = i
            
        data.set_index('count',drop=True,inplace=True)
        
        index_missing = list()

        for i in range(1,data.shape[0]):
            try:
                index_missing.append(
                    data['change'].index[data['change'].apply(np.isnan)][i]
                )
                
            except Exception as e:
                pass
        index_missing.append(data['change'][data.shape[0] - 1])
        
        change_index = list()
        
        for i in range(len(index_missing) - 1):
            change_index.append(data['change'][index_missing[i] - 1])
            
        change_index.append(data['change'][data.shape[0] - 1])
        
        self.buy_sell_data['change'] = change_index
        
        
        
        return self.buy_sell_data
        #return data
   
      