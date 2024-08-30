import FinanceDataReader as fdr
from fbprophet import Prophet
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import time
from sys01.sys01_base import *


def apply_prophet(df, past_offset, fcast_time):
    df_prophet = Prophet(changepoint_range=0.8, changepoint_prior_scale=0.15, daily_seasonality=False, yearly_seasonality=False,
                         weekly_seasonality=False)
    if past_offset > 0:
        df = df.iloc[:-past_offset]
    df_prophet.fit(df)
    future = df_prophet.make_future_dataframe(periods=(fcast_time + past_offset), freq="D")
    forecast = df_prophet.predict(future)
    return forecast

class sys01_process:
    def __init__(self, file_name, years, fcast_time, past_offset):
        self.file_name = file_name
        self.years = years
        self.fcast_time = fcast_time
        self.past_offset = past_offset


    def my_apply_prophet(self, save_raw_path):
        file_name = self.file_name
        years = self.years # '2023' str Type
        fcast_time = self.fcast_time # 10 int Type
        # 일주일전 데이터가지고 이번주 데이터 예측하기 위한 offset = 5 * (내가 원하는 주차까지)
        past_offset = self.past_offset # 10 int Type
        today =  datetime.today().strftime("%Y%m%d")
        # 입력변수는 여기까지
        processed_data_col = ['code', 'name', 'ds', 'y']
        processed_data_col = append_col(processed_data_col, "t", past_offset+1)    
        processed_data_col = append_col(processed_data_col, "del", past_offset)
        processed_data_col.append("bool")  
        
        processed_data = pd.DataFrame(columns=processed_data_col)

        name_code_df = pd.read_excel(file_name, engine='openpyxl')

        # 가격 정보 먼저 가져와서 오프라인 환경에서도 계산 가능하게
        get_price_data(name_code_df, years, save_raw_path)
        
        for year in years:
            year_raw_data_path = save_raw_path + "/" + year
            makedirs(year_raw_data_path)
            today = datetime.today().strftime("%Y%m%d")                

            for num_stock in range(len(name_code_df)):
                stock_name = name_code_df.loc[num_stock]['종목명']
                stock_code = str(name_code_df.loc[num_stock]['Code']).zfill(6)

                save_price_data_path = year_raw_data_path + "/price"
                save_price_file = save_price_data_path + "/" + f"{year}_{stock_code}_{today}_price.xlsx"

                # 데이터 원천은 여기임 / 오프라인 환경에서도 할 수 있게 먼저 가격정보 가져오기 line 48 볼 것!!
                data = pd.read_excel(save_price_file, engine="openpyxl")
                # data = fdr.DataReader(stock_code, year)['Close']

                save_raw_data_file = f"{year}_{stock_code}_{today}.xlsx"
                save_raw_data_path = year_raw_data_path + "/" + save_raw_data_file

                r_df = pd.DataFrame()
                r_df['ds'] = data['Date']
                r_df['y'] = data['Close']
                t_df = r_df.copy()
                training_df = r_df.copy()

                i = 0
                with pd.ExcelWriter(save_raw_data_path) as writer:
                    for i in range(past_offset+1):
                        forecast = apply_prophet(training_df, i, fcast_time)
                        forecast.to_excel(writer, sheet_name=str(i), index=False)

                        local_prediction = forecast['yhat'].to_frame()
                        r_df = pd.concat([r_df, local_prediction], axis=1)

                        local_trend = forecast['trend'].to_frame()
                        t_df = pd.concat([t_df, local_trend], axis=1)

                    # use to_excel function and specify the sheet_name and without index
                    r_df.to_excel(writer, sheet_name="real_data", index=False)
                    t_df.to_excel(writer, sheet_name="trend_data", index=False)

                    local_price_info = r_df.iloc[-1-fcast_time , 0:2]
                    local_trend_tangent1 = t_df.iloc[-1 ,2:8]
                    local_trend_tangent2 = t_df.iloc[-2 ,2:8]
                    
                    local_trend_tangent = local_trend_tangent1.sub(local_trend_tangent2).tolist()
                    local_trend_tangent_del = []
                    for ltt in range(len(local_trend_tangent)-1):
                        local_del = local_trend_tangent[ltt]-local_trend_tangent[ltt+1]
                        local_trend_tangent_del.append(local_del)
                    
                    del_bool = all(num>0 for num in local_trend_tangent_del)

                    here_info = [stock_code, stock_name]
                    here_info.extend(local_price_info)
                    here_info.extend(local_trend_tangent)
                    here_info.extend(local_trend_tangent_del)
                    here_info.append(del_bool)

                    processed_data.loc[num_stock] = here_info

            save_processed_file_name = f"{year}_total_{str(past_offset)}_{today}.xlsx"
            save_processed_file_path = save_raw_path + '/' + save_processed_file_name
            processed_data.to_excel(save_processed_file_path , index=False)
        return processed_data




