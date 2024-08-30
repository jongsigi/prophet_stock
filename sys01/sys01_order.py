import FinanceDataReader as fdr
from fbprophet import Prophet
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from sys01.sys01_base import *
from sys01.sys01_process import *


def sys01_order(year, fcast_time, past_offset, save_filtered_path, capital):
    year = year # '2023' str Type
    fcast_time = fcast_time # 10 int Type
    # 일주일전 데이터가지고 이번주 데이터 예측하기 위한 offset = 5 * (내가 원하는 주차까지)
    past_offset = past_offset # 10 int Type
    today =  datetime.today().strftime("%Y%m%d")
    # 입력변수는 여기까지

    order_data = pd.DataFrame(columns= ['Code','name','ds', 'y', 'yhat_1', 'predict_1'])
    save_filtered_file = save_filtered_path + "/filtered_target.xlsx"
    name_code_df = pd.read_excel(save_filtered_file, engine='openpyxl')

    filtered_raw_path = save_filtered_path +'/filtered' 
    
    for num_stock in range(len(name_code_df)): 
        stock_name = name_code_df.loc[num_stock]['name']
        # if name_code_df.loc[num_stock]['code'].isalpha():
        #     stock_code = name_code_df.loc[num_stock]['code']
        # else:
        #     stock_code = str(name_code_df.loc[num_stock]['code']).zfill(6)
        stock_code = str(name_code_df.loc[num_stock]['code']).zfill(6)
        makedirs(filtered_raw_path)

        filtered_raw_file = f"{year}_{stock_code}_{today}.xlsx"

        r_df = pd.DataFrame()
        delta_df = pd.DataFrame()
        output_df = pd.DataFrame()

        # 데이터 원천은 여기임
        data = fdr.DataReader(stock_code, year)['Close']

        r_df['ds'] = data.index
        r_df['y'] = data.values
        output_df['ds'] = r_df['ds']
        output_df['y'] = r_df['y']

        # delta로 데이터 전처리
        delta_df['ds'] = r_df['ds']
        delta_df['y'] = r_df['y'].diff()

        dataframe_lists = [delta_df]
        i=1

        with pd.ExcelWriter(filtered_raw_path+'/'+filtered_raw_file) as writer:
            # [실제 값, Delta, Delat %] 에 의한 예측 값들을 모아서 하나의 Sheet에 저장하기 위한 For 문
            # 0 = 실제값 , 1 = delta , 2 = detla %에 의한 예측
            for df in dataframe_lists:            
                forcast = apply_prophet(df, past_offset, fcast_time)
                forcast.to_excel(writer, sheet_name = str(i), index=False)

                a = forcast['yhat'].to_frame()
                r_df = pd.concat([r_df, a], axis=1)

                if i == 0:
                    pass
                    # predict_0 = forcast['yhat'].to_frame()
                    # predict_0.columns = ['predict_0']
                    # output_df = pd.concat([output_df,predict_0],axis=1)

                elif i == 1:
                    temp_output1 = []
                    for j in range(len(forcast)):
                        if j == 0:
                            output1 = r_df['y'][0] + forcast['yhat'][0]
                            temp_output1.append(output1)
                        else:
                            output1_2 = temp_output1[j-1] + forcast['yhat'][j]
                            temp_output1.append(output1_2)
                        
                    add_df1 = pd.DataFrame(temp_output1, columns=['predict_1'])
                    output_df = pd.concat([output_df,add_df1],axis=1)

                # elif i == 2:
                #     temp_output2 = []
                #     for j in range(len(forcast)):
                #         if j == 0:
                #             output2 = r_df['y'][0] * (1 + forcast['yhat'][0])
                #             temp_output2.append(output2)
                #         else:
                #             output2_2 = temp_output2[j-1] * (1+ forcast['yhat'][j])
                #             temp_output2.append(output2_2)
                #     add_df2 = pd.DataFrame(temp_output2, columns=['predict_2'])
                #     output_df = pd.concat([output_df,add_df2],axis=1)
                    
                i+=1

            # use to_excel function and specify the sheet_name and without index
            r_df.to_excel(writer, sheet_name="real_data", index=False)
            output_df.to_excel(writer, sheet_name="output_data", index=False)

            # 가장 끝 값 = 예측하고자하는 날의 가격
            here_future = output_df.iloc[-1,2:3].to_list()
            # 가장 끝에서 fcast_time 전은 당일날 가격을 어떻게 예측했는지 체크
            here_now = output_df.iloc[-1- fcast_time].to_list() 
            here_now.extend(here_future)

            here_info = [stock_code, stock_name]
            here_info.extend(here_now)

            order_data.loc[num_stock] = here_info

    order_data['PROI'] = order_data['predict_1']/order_data['yhat_1'] - 1
    order_data['EROI'] = order_data['predict_1']/order_data['y'] - 1
    order_data['ROI'] = order_data.min(axis=1, numeric_only=True)

    order_data = order_data[order_data['ROI']>0.02]
    if len(order_data)>7:
        order_data = order_data.nlargest(8,"ROI",keep='first')

    order_stock_num = len(order_data)
    input_money = round(capital/order_stock_num, -3)
    order_data['Qty'] = round(input_money/order_data['y'])

    avg_ROI = order_data['ROI'].mean()
    stop_per = avg_ROI/3
    order_data['Stop'] = round((1-stop_per)*order_data['y'] , -2)
    order_data['Sell'] = round((1 + order_data['ROI']) * order_data['y'] , -2)

    display_per = ['PROI', 'EROI', 'ROI']
    for per_col in display_per:
        order_data.style.format({per_col:'{:.2%}'.format})

    evaluation_file_name = f"{year}_order_{fcast_time}_{today}.xlsx"
    order_data.to_excel(save_filtered_path +'/'+evaluation_file_name , index=False)
    return order_data



