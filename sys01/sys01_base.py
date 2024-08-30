import FinanceDataReader as fdr
from datetime import datetime
import os
import pandas as pd

def get_week_number():
    today = datetime.today().strftime('%Y-%m-%d')
    year, week_number, _ = datetime.strptime(today, '%Y-%m-%d').isocalendar()
    return week_number #Return int Type\

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def append_col(base, add_word ,add_num):
    for add_num_col in range(add_num):
        local_add_num_col = f"{add_word}{str(add_num_col)}"
        base.append(local_add_num_col)
    return base

# 240708 가격을 먼저 저장하기 위한 가격 기록 저장용 코드
def get_price_data(name_code_df,years, save_raw_path):
    today = datetime.today().strftime("%Y%m%d") 
    name_code_df = name_code_df

    for year in years:  
        save_price_data_path = save_raw_path + "/" + year + "/price"  
        makedirs(save_price_data_path)

        for num_stock in range(len(name_code_df)):
            stock_code = str(name_code_df.loc[num_stock]['Code']).zfill(6)
            price_data = fdr.DataReader(stock_code, year)['Close']
            save_price_file = save_price_data_path + "/" +f"{year}_{stock_code}_{today}_price.xlsx"
            price_data.to_excel(save_price_file)