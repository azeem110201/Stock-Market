import streamlit as st
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import plotly.express as px
import datetime
import plotly.graph_objects as go
from ModelAnalysis import ModelAnalysis
import sqlite3
import base64



def main(ticker_name_list):
    today = datetime.date.today()
    prev = today - datetime.timedelta(days=365)
    curr = datetime.date.today()
    start_date = st.date_input('Start date', prev)
    end_date = st.date_input('End date', curr)
    
    if start_date < end_date:
        stock_name = st.selectbox(label='Select Stock ticker:',options=ticker_name_list)
        
        MA = ModelAnalysis(start_date, end_date, stock_name)
        data = MA.get_stock_name()
        st.write("Stocks for previous 14 Days.....")
        st.write(data.tail(14))
        
        def get_table_download_link(df):
            """Generates a link allowing the data in a given panda dataframe to be downloaded
            in:  dataframe
            out: href string
            """
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(
                csv.encode()
            ).decode()  # some strings <-> bytes conversions necessary here
            
            return f'<a href="data:file/csv;base64,{b64}" download="mypredications.csv">Download the above table in the form of csv</a>'
        
        st.markdown(get_table_download_link(data), unsafe_allow_html=True)
        
        stock_column = st.selectbox(label='Select Stock Column from above data:',options=data.columns)
        stock_column = str(stock_column)
        
        fig = MA.get_plot(stock_column)
        
        agree = st.checkbox("Plot")
        
        if agree:
            if fig is None:
                st.write('The name is not valid.Please check the name')
            else:
                st.plotly_chart(fig)
                
                
        agree_compare_stocks = st.checkbox("Compare stocks. Make sure that all the letter are upper case")
        
        if agree_compare_stocks:
            user_input_compare = st.text_input("Write Stock Ticker separate by comma's ")
            if user_input_compare:
                user_input_compare = str(user_input_compare)
                user_input_compare = user_input_compare.split(",")
                fig, no_stocks = MA.compare_stocks(user_input_compare)
                if fig is None or user_input_compare is None:
                    st.write("data for the stocks given is not available")
                else:
                    st.plotly_chart(fig)
                    for i in no_stocks:
                        st.write('<font color="blue"> No stock data available for {}</font>'.format(i),unsafe_allow_html=True\
                                    )
        
     
        add_ewa_sma = st.checkbox("Plot Expotential Moving Average for the stock select") 
        
        if add_ewa_sma:
            #window_size = st.number_input("Enter window size of stock")
            st.write(
                "An exponential moving average (EMA) is a type of moving average (MA) that places a greater weight and significance on the most recent data points. EMA gives the direction in which the stocks is going."
            )
            fig = MA.ewa_sma()
            if fig is None:
                st.write('The name is not valid.Please check the name')
            else:
                st.plotly_chart(fig)
                
        candle_plot = st.checkbox("Plot Candle Plot for the stock select") 
        
        if candle_plot:
            #window_size = st.number_input("Enter window size of stock")
            fig = MA.candle_plot()
            if fig is None:
                st.write('The name is not valid.Please check the name')
            else:
                st.plotly_chart(fig)    
                
        buy_sell = st.checkbox("See when to buy or sell stocks. Make sure that all the letter are upper case")
        
        if buy_sell:
            user_input = st.text_input("Stock Ticker separate by comma's ")
            if user_input:
                user_input = str(user_input)
                user_input = user_input.split(",")
                details = MA.buy_sell(user_input)
                if details is None or user_input is None:
                    st.write("data for the stocks given is not available")
                else:
                    st.write(details)
                    if len(details['Ticker'].unique()) != len(user_input):
                        ticker_missing = set(user_input).difference(details['Ticker'].unique())
                        for i in ticker_missing:
                            st.write('<font color="blue"> No stock data available for {}</font>'.format(i),unsafe_allow_html=True\
                                    )
                    st.markdown(get_table_download_link(details), unsafe_allow_html=True)   
                    
                    
        about_me = st.checkbox("Click here to know about me")
        
        if about_me:
            st.markdown("**Github Profile:**")
            st.markdown("[Mohd Abdul Azeem](https://github.com/azeem110201)")
            st.markdown('<font color="red">Student,from Hyderabad</font>',unsafe_allow_html=True)        

    else:
        st.warning("Start end should be less than end date")


if __name__ == "__main__":
    
    database = 'ticker.db'
    
    st.title('Stock Market Analysis')
    
    st.image("stock_market3.jpg",width=700)
    
    st.info(''' Welcome to our WebApp where you can analyse and take decision regarding stocks with more than 450+ stock tickers ''')
    
    st.markdown('**Make sure that start date is less than end date**.')
    
    
    conn = sqlite3.connect(database)

    df = pd.read_sql_query("select * from sqlite_master where tbl_name ='stock_ticker' ", con=conn)

    st_names = pd.read_sql_query("""
        SELECT * 
        FROM stock_ticker;
    """,conn)
    
    ticker_name_list = list()

    for i in range(st_names.shape[0]):
        ticker_name_list.append(st_names['Tickers'][i])
    
    main(ticker_name_list)
    
    conn.close()
